import os

import json
import requests
import openai

from env import OPENAI_API_KEY, OPENAI_MODEL

client = openai.OpenAI()
client.api_key = OPENAI_API_KEY


DOWNLOAD_TEMP_FILE = "/tmp/paper.pdf"


def download_pdf(url: str) -> bool:
    response = requests.get(url)
    if response.status_code == 200:
        with open(DOWNLOAD_TEMP_FILE, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download PDF: {response.status_code}")
        return False


def delete_temp_file():
    try:
        os.remove(DOWNLOAD_TEMP_FILE)
    except OSError as e:
        print(f"Error deleting temp file: {e}")


def generate_summary(pdf: str) -> (
    tuple[
        list[dict[str, str]],
        list[str],
    ]
    | None
):
    if not download_pdf(pdf):
        return None

    # Upload the PDF file
    file = client.files.create(
        file=open(DOWNLOAD_TEMP_FILE, "rb"),
        purpose="assistants",
    )

    delete_temp_file()

    system_instruction = """\
あなたは論文を要約するためのAIです。\
出力はresponse_formatに従って記述してください。\
"""

    instruction = """\
# task: 添付した論文を以下の項目で要約してください。
各項目ごとに設定されている注意点・文字数に従って記述してください。
なお、論文中の専門単語を無理に日本語に訳さず、英語のまま使用してください。

## 背景
    - 発表時点での研究状況と問題点
    - 5文程度
## 概要
    - 論文全体の概要
    - 10文程度
## 新規性・差分
    - 他の研究との比較
    - 10文程度
## 手法
    - 論文が提案する事項
    - 重要な手法やアルゴリズムを含める
    - 一番重要なので詳細に記述
    - 20文程度
## 結果
    - 論文の結果
    - 著者が特に重要だと考える結果を記述
    - 10文程度
## 議論
    - 著者が考える結果に対する考察
    - 10文程度

# output format
{
    "sections": [
        {
            "section": "項目名 例: 背景",
            "content": "要約内容"
        },
        ...
    ]
}
"""

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "text",
                        "text": system_instruction,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {"file_id": file.id},
                    },
                    {
                        "type": "text",
                        "text": instruction,
                    },
                ],
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "paper_summary",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "section": {
                                        "type": "string",
                                        "description": "項目名 例: 背景",
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "要約内容",
                                    },
                                },
                                "required": ["section", "content"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["sections"],
                    "additionalProperties": False,
                },
            },
        },
    )
    # Extract the summary from the response
    summary = json.loads(completion.choices[0].message.content)["sections"]

    system_instruction = """\
あなたは論文を解析するためのAIです。\
出力はresponse_formatに従って記述してください。\
"""
    instruction = """\
# task: 添付した論文からキーワード・トピックを10個抽出してください。

# output format
{
    "keywords": [
        "keyword1",
        "keyword2",
        ...
    ]
}
"""

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "text",
                        "text": system_instruction,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {"file_id": file.id},
                    },
                    {
                        "type": "text",
                        "text": instruction,
                    },
                ],
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "paper_keywords",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "キーワード",
                            },
                        },
                    },
                    "required": ["keywords"],
                    "additionalProperties": False,
                },
            },
        },
    )
    # Extract the keywords from the response
    keywords = json.loads(completion.choices[0].message.content)["keywords"]

    client.files.delete(file.id)
    return summary, keywords


if __name__ == "__main__":
    from pprint import pprint

    pdf_url = "https://arxiv.org/pdf/1706.03762"  # Attention Is All You Need
    summary, keywords = generate_summary(pdf_url)

    print("Summary:")
    pprint(summary)
    print("\nKeywords:")
    pprint(keywords)
