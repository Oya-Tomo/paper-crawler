import datetime
from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

from summarizer.database import Session, Paper


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
    session = Session()

    # Check if the paper already exists
    existing_paper = session.query(Paper).filter_by(id=request.id).first()
    if existing_paper is not None:
        return StatusResponse(status=Status.failed, message="Paper already exists")

    paper = Paper(
        id=request.id,
        title=request.title,
        abstract=request.abstract,
        authors=request.authors,
        organizations=request.organizations,
        url=request.url,
        pdf=request.pdf,
        journal=request.journal,
        doi=request.doi,
        published_at=request.published_at,
        updated_at=request.updated_at,
    )
    session.add(paper)
    session.commit()

    return StatusResponse(status=Status.ok, message="Paper created successfully")


class GetPaperRequest(BaseModel):
    id: str


class GetPaperResponse(BaseModel):
    status: Status
    message: str
    paper: Paper | None


@server.get("/get", response_model=GetPaperResponse)
async def get_paper(request: GetPaperRequest):
    session = Session()

    paper = session.query(Paper).filter_by(id=request.id).first()
    if paper is None:
        return GetPaperResponse(
            status=Status.failed, message="Paper not found", paper=None
        )

    return GetPaperResponse(status=Status.ok, message="Paper found", paper=paper)


class GetPaperListResponse(BaseModel):
    status: Status
    message: str
    papers: list[Paper]


@server.get("/list", response_model=GetPaperListResponse)
async def get_paper_list():
    session = Session()

    papers = session.query(Paper).all()
    if not papers:
        return GetPaperListResponse(
            status=Status.failed, message="No papers found", papers=[]
        )

    return GetPaperListResponse(status=Status.ok, message="Papers found", papers=papers)


class UpdatePaperRequest(BaseModel):
    id: str

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
    session = Session()

    paper = session.query(Paper).filter_by(id=request.id).first()
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
        status=Status.ok, message="Paper updated successfully", paper=paper
    )
