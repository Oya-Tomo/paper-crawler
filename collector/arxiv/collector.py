import datetime
import xml.etree.ElementTree as ET

import requests
from pydantic import BaseModel
from typing import Self

from arxiv.api import xml_to_arxiv_json, url_to_arxiv_id


class ArxivPaper(BaseModel):
    id: str
    src: str = "arxiv"

    title: str
    abstract: str

    authors: list[str]
    organizations: list[str]

    url: str
    pdf: str

    journal: str | None
    doi: str | None

    published_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def from_dict(self, data: dict) -> Self:
        return ArxivPaper(
            id=url_to_arxiv_id(data["id"]),
            title=data["title"],
            abstract=data["summary"],
            authors=[author["name"] for author in data["authors"]],
            organizations=list(
                set(author["affiliation"] for author in data["authors"]) - {None}
            ),
            url=data["id"],
            pdf=data["pdf"],
            journal=data["journal_ref"],
            doi=data["doi"],
            published_at=datetime.datetime.fromisoformat(data["published"]),
            updated_at=datetime.datetime.fromisoformat(data["updated"]),
        )


def collect_arxiv_papers(
    search_query: str | None = None,
    id_list: str | None = None,
    start: int = 0,
    max_results: int = 10,
) -> list[ArxivPaper]:
    base_url = f"http://export.arxiv.org/api/query?"
    params = []
    if search_query is not None:
        params.append(f"search_query={search_query}")
    if id_list is not None:
        params.append(f"id_list={id_list}")
    params.append(f"start={start}")
    params.append(f"max_results={max_results}")
    url = base_url + "&".join(params)

    response = requests.get(url)
    xml = ET.fromstring(response.text)
    data = xml_to_arxiv_json(xml)

    return [ArxivPaper.from_dict(paper) for paper in data]


if __name__ == "__main__":
    query = None
    id_list = "2503.21782"
    start = 0
    max_results = 10
    papers = collect_arxiv_papers(
        search_query=query,
        id_list=id_list,
        start=start,
        max_results=max_results,
    )

    for paper in papers:
        print(paper.model_dump_json(indent=2))
