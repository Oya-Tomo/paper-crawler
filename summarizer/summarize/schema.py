import pprint
from pydantic import BaseModel, Field
from typing import Literal


class ElementSchema(BaseModel, extra="forbid"):
    type: Literal["text", "table", "katex"] = Field(
        ..., description="Type of the element"
    )
    content: str = Field(
        ...,
        description="Content of the element. "
        "(text: plain text (includes markdown bold/italic/strike span), "
        "table: csv, "
        "katex: latex formula)",
    )

    def to_markdown(self) -> str:
        if self.type == "text":
            return self.content
        elif self.type == "table":
            return f"```csv\n{self.content}\n```"
        elif self.type == "katex":
            return f"$${self.content}$$"
        else:
            raise ValueError(f"Unknown element type: {self.type}")


class SubsectionSchema(BaseModel, extra="forbid"):
    title: str = Field(..., description="Title of the subsection")
    contents: list[ElementSchema] = Field(
        ..., description="List of subsection contents"
    )

    def to_markdown(self) -> str:
        return "\n".join(
            [
                f"### {self.title}",
                "\n".join([content.to_markdown() for content in self.contents]),
            ]
        )


class SectionSchema(BaseModel, extra="forbid"):
    title: str = Field(..., description="Title of the section")
    contents: list[ElementSchema] = Field(..., description="List of section contents")
    subsections: list[SubsectionSchema] = Field(
        ..., description="List of subsections in the section"
    )

    def to_markdown(self) -> str:
        return "\n\n".join(
            [
                "\n".join(
                    [
                        f"## {self.title}",
                        "\n".join([content.to_markdown() for content in self.contents]),
                    ]
                )
            ]
            + [
                subsection.to_markdown()
                for subsection in self.subsections
                if subsection.contents
            ]
        )


class DocumentSchema(BaseModel, extra="forbid"):
    sections: list[SectionSchema] = Field(
        ..., description="List of sections in the document"
    )

    def to_markdown(self) -> str:
        return "\n\n".join([section.to_markdown() for section in self.sections])


class KeywordsSchema(BaseModel, extra="forbid"):
    keywords: list[str] = Field(..., description="List of keywords in the document")


if __name__ == "__main__":
    pprint.pprint(DocumentSchema.model_json_schema())
