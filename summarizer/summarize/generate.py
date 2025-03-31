import os

import json
import requests
import openai

from schema import DocumentSchema, SectionSchema, KeywordsSchema

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL environment variable is not set.")


client = openai.OpenAI()
client.api_key = OPENAI_API_KEY


def download_pdf(url: str, path: str) -> bool:
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download PDF: {response.status_code}")
        return False


def delete_temp_file(path: str):
    try:
        os.remove(path)
    except OSError as e:
        print(f"Error deleting temp file: {e}")


def generate_completion(
    file_id: str,
    system_prompt: str,
    user_prompt: str,
    response_schema: dict,
) -> dict:
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {"file_id": file_id},
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document_schema",
                "strict": True,
                "schema": response_schema,
            },
        },
    )
    return json.loads(completion.choices[0].message.content)


def generate_summary(id: str, src: str, pdf: str) -> tuple[str, list[str]] | None:
    try:
        download_path = f"/tmp/paper-{\
                id.replace("/", "%").replace(".", "_")\
            }-{\
                src.replace('/', '%').replace('.', '_')\
            }.pdf"

        if not download_pdf(pdf, download_path):
            return None

        with open(download_path, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="assistants",
            )

        delete_temp_file(download_path)

        section_outputs: list[SectionSchema] = []

        # Common system prompt for all sections

        system_prompt = """\
# Task: Thesis/Paper/Article analysis
論文の添付ファイルを基に、ユーザーの命令に従って論文から情報を要約・抽出してください。

# Response format: Use given Json schema
論文の要約をJson schemaに従って出力してください。

# Language: Japanese
項目名や内容は日本語で記載してください。ただし、論文中にある英語の用語はそのまま使用してください。

# Background: Making a summary report of the thesis
ユーザーの論文の要約レポートを補助して下さい。
"""

        # Generate summary of all sections

        user_prompt = """\
# Task: Generate summary from Thesis/Paper/Article
この論文の概要について教えてください。
このセクションは「概要」セクションに相当します。
ここでは構造的な文章よりも、論文全体の流れをつかめるような要約をしてください。

# Response format: Use given Json schema
section.title: 概要
section.contents: 論文中の「abstract/summary/background」の要約
section.subsections: empty
"""

        output = generate_completion(
            file_id=file.id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=SectionSchema.model_json_schema(),
        )
        section_outputs.append(SectionSchema.model_validate(output))

        # Generate summary of difference from previous works

        user_prompt = """\
# Task: Generate summary from Thesis/Paper/Article
このセクションは「新規性・差分」セクションに相当します。
論文中で述べられる既存手法との違いや提案手法のメリット・デメリットを基に詳しくまとめてください。
読みやすいように、構造的な文章で要約してください。

# Output format: Use given Json schema
section.title: 新規性・差分
section.contents: 論文中の「新規性・差分」の概要
section.subsections: 「新規性・差分」の各サブセクション
section.subsections[].title: サブセクションのタイトル
section.subsections[].contents: サブセクションの概要
"""

        output = generate_completion(
            file_id=file.id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=SectionSchema.model_json_schema(),
        )
        section_outputs.append(SectionSchema.model_validate(output))

        # Generate summary of methods

        user_prompt = """\
# Task: Generate summary from Thesis/Paper/Article
このセクションは「手法」セクションに相当します。
論文が提案している概念・手法・実施した実験について、論文の論述の流れを基に詳しく教えてください。
数式や表、疑似コードなどは、なるべく省略せずに記載してください。
読みやすいように、構造的な文章で要約してください。

# Output format: Use given Json schema
section.title: 手法
section.contents: 論文中の「手法」の概要
section.subsections: 論文中の「手法」の各サブセクション
section.subsections[].title: サブセクションのタイトル
section.subsections[].contents: サブセクションの概要
"""

        output = generate_completion(
            file_id=file.id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=SectionSchema.model_json_schema(),
        )
        section_outputs.append(SectionSchema.model_validate(output))

        # Generate summary of results

        user_prompt = """\
# Task: Generate summary from Thesis/Paper/Article
このセクションは「結果」セクションに相当します。
論文中で述べられる実験結果や評価結果を基に詳しくまとめてください。
特に、筆者が強調しているポイントや、実験結果の解釈についても詳しく教えてください。
読みやすいように、構造的な文章で要約してください。

# Output format: Use given Json schema
section.title: 結果
section.contents: 論文中の「結果」の概要
section.subsections: 「結果」の各サブセクション
section.subsections[].title: サブセクションのタイトル
section.subsections[].contents: サブセクションの概要
"""

        output = generate_completion(
            file_id=file.id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=SectionSchema.model_json_schema(),
        )
        section_outputs.append(SectionSchema.model_validate(output))

        # Extract keywords
        system_prompt = """\
# Task: Thesis/Paper/Article analysis
論文の添付ファイルを基に、ユーザーの命令に従って論文から情報を要約・抽出してください。
"""

        user_prompt = """\
# Task: Extract keywords or topics from Thesis/Paper/Article
この論文のキーワードやトピックを10個以上抽出してください。" \
"""

        output = generate_completion(
            file_id=file.id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=KeywordsSchema.model_json_schema(),
        )

        client.files.delete(file.id)

        return (
            DocumentSchema(sections=section_outputs).to_markdown(),
            KeywordsSchema.model_validate(output).keywords,
        )

    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


if __name__ == "__main__":
    from pprint import pprint

    pdf_url = "https://arxiv.org/pdf/1706.03762"  # Attention Is All You Need
    summary, keywords = generate_summary("1706.03762", "arxiv", pdf_url)

    print("# Keywords")
    print(keywords)
    print()
    print("# Summary")
    print(summary)
