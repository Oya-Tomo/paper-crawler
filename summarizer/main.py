import datetime
from enum import Enum
from typing import Literal

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select

from model import Paper, PaperSource
from database import Session, PaperRow
from summarize import generate_summary


server = FastAPI(
    title="Paper Summarizer",
    description="API for summarizing papers.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Common Response Models


class Status(str, Enum):
    ok = "ok"
    failed = "failed"
    error = "error"


class StatusResponse(BaseModel):
    status: Status
    message: str


# Endpoints


class CreatePaperRequest(BaseModel):
    id: str
    src: PaperSource

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


@server.post("/create", response_model=StatusResponse)
async def create_paper(request: CreatePaperRequest):
    with Session() as session:
        exsiting_paper = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == request.id)
            .where(PaperRow.src == request.src),
        )
        if exsiting_paper is not None:
            return StatusResponse(status=Status.failed, message="Paper already exists")

        paper = PaperRow(
            id=request.id,
            src=request.src,
            title=request.title,
            abstract=request.abstract,
            authors=request.authors,
            organizations=request.organizations,
            url=request.url,
            pdf=request.pdf,
            journal=request.journal,
            doi=request.doi,
            topics=None,
            summary=None,
            published_at=request.published_at,
            updated_at=request.updated_at,
        )
        session.add(paper)
        session.commit()

        return StatusResponse(status=Status.ok, message="Paper created successfully")


class GetPaperRequest(BaseModel):
    id: str
    src: PaperSource


class GetPaperResponse(BaseModel):
    status: Status
    message: str
    paper: Paper | None


@server.get("/get", response_model=GetPaperResponse)
async def get_paper(request: GetPaperRequest):
    with Session() as session:
        paper = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == request.id)
            .where(PaperRow.src == request.src),
        )
        if paper is None:
            return GetPaperResponse(
                status=Status.failed, message="Paper not found", paper=None
            )

        return GetPaperResponse(
            status=Status.ok,
            message="Paper found",
            paper=Paper.from_sql(paper),
        )


class SearchQuery(BaseModel):
    column: Literal[
        "id",
        "src",
        "title",
        "abstract",
        "authors",
        "organizations",
        "url",
        "journal",
        "doi",
        "topics",
        "published_at",
        "updated_at",
    ]
    value: str


class SearchPaperRequest(BaseModel):
    queries: list[SearchQuery]
    limit: int | None = None
    offset: int | None = None


class SearchPaperResponse(BaseModel):
    status: Status
    message: str
    papers: list[Paper]


@server.post("/search", response_model=SearchPaperResponse)
async def search_paper(request: SearchPaperRequest):
    with Session() as session:
        query = select(PaperRow)
        for search_query in request.queries:
            if search_query.column == "id":
                query = query.where(
                    PaperRow.id.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "src":
                query = query.where(
                    PaperRow.src.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "title":
                query = query.where(
                    PaperRow.title.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "abstract":
                query = query.where(
                    PaperRow.abstract.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "authors":
                query = query.where(
                    PaperRow.authors.any().ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "organizations":
                query = query.where(
                    PaperRow.organizations.any().ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "url":
                query = query.where(
                    PaperRow.url.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "journal":
                query = query.where(
                    PaperRow.journal.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "doi":
                query = query.where(
                    PaperRow.doi.ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "topics":
                query = query.where(
                    PaperRow.topics.any().ilike(f"%{search_query.value}%"),
                )
            elif search_query.column == "published_at":
                query = query.where(
                    PaperRow.published_at
                    == datetime.datetime.strptime(
                        search_query.value,
                        "%Y-%m-%d %H:%M:%S.%f",
                    ),
                )
            elif search_query.column == "updated_at":
                query = query.where(
                    PaperRow.updated_at
                    == datetime.datetime.strptime(
                        search_query.value,
                        "%Y-%m-%d %H:%M:%S.%f",
                    ),
                )
            else:
                return SearchPaperResponse(
                    status=Status.error,
                    message="Invalid query column",
                    papers=[],
                )

        if request.limit is not None:
            query = query.limit(request.limit)
        if request.offset is not None:
            query = query.offset(request.offset)

        papers = session.scalars(query).all()

        return SearchPaperResponse(
            status=Status.ok,
            message="Papers searched successfully",
            papers=[Paper.from_sql(paper) for paper in papers],
        )


class SummarizePaperRequest(BaseModel):
    id: str
    src: PaperSource


class SummarizePaperResponse(BaseModel):
    status: Status
    message: str
    topics: list[str] | None
    summary: str | None


def summarize_paper_on_background(paper: Paper):
    result = generate_summary(paper.pdf)
    if result is None:
        print("Failed to generate summary")
        return
    summary, topics = result

    with Session() as session:
        paper_row = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == paper.id)
            .where(PaperRow.src == paper.src),
        )
        if paper_row is None:
            return

        paper_row.topics = topics
        paper_row.summary = "\n\n".join(
            [f"## {sect["section"]}\n{sect["content"]}" for sect in summary]
        )
        session.commit()
        print("Summary generated successfully")


@server.post("/summarize", response_model=StatusResponse)
async def summarize_paper(
    request: SummarizePaperRequest,
    background_tasks: BackgroundTasks,
):
    with Session() as session:
        paper = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == request.id)
            .where(PaperRow.src == request.src),
        )
        if paper is None:
            return StatusResponse(
                status=Status.failed,
                message="Paper not found",
            )

        background_tasks.add_task(summarize_paper_on_background, Paper.from_sql(paper))
        return StatusResponse(
            status=Status.ok,
            message="Paper is being summarized",
        )


class UpdatePaperRequest(BaseModel):
    id: str
    src: PaperSource

    title: str | None
    abstract: str | None

    authors: list[str] | None
    organizations: list[str] | None

    url: str | None
    pdf: str | None

    journal: str | None
    doi: str | None

    published_at: datetime.datetime | None
    updated_at: datetime.datetime | None


class UpdatePaperResponse(BaseModel):
    status: Status
    message: str
    paper: Paper | None


@server.put("/update", response_model=UpdatePaperResponse)
async def update_paper(request: UpdatePaperRequest):
    with Session() as session:
        paper = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == request.id)
            .where(PaperRow.src == request.src),
        )
        if paper is None:
            return UpdatePaperResponse(
                status=Status.failed, message="Paper not found", paper=None
            )

        if request.title is not None:
            paper.title = request.title
        if request.abstract is not None:
            paper.abstract = request.abstract
        if request.authors is not None:
            paper.authors = request.authors
        if request.organizations is not None:
            paper.organizations = request.organizations
        if request.url is not None:
            paper.url = request.url
        if request.pdf is not None:
            paper.pdf = request.pdf
        if request.journal is not None:
            paper.journal = request.journal
        if request.doi is not None:
            paper.doi = request.doi
        if request.published_at is not None:
            paper.published_at = request.published_at
        if request.updated_at is not None:
            paper.updated_at = request.updated_at

        session.commit()

        return UpdatePaperResponse(
            status=Status.ok,
            message="Paper updated successfully",
            paper=Paper.from_sql(paper),
        )


class DeletePaperRequest(BaseModel):
    id: str
    src: PaperSource


@server.delete("/delete", response_model=StatusResponse)
async def delete_paper(request: DeletePaperRequest):
    with Session() as session:
        paper = session.scalar(
            select(PaperRow)
            .where(PaperRow.id == request.id)
            .where(PaperRow.src == request.src),
        )
        if paper is None:
            return StatusResponse(
                status=Status.failed,
                message="Paper not found",
            )

        session.delete(paper)
        session.commit()

        return StatusResponse(
            status=Status.ok,
            message="Paper deleted successfully",
        )
