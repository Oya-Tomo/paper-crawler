from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI
from pydantic import BaseModel

from arxiv.collector import collect_arxiv_papers, ArxivPaper


def startup():
    print("Starting up the server...")


def shutdown():
    print("Shutting down the server...")


@asynccontextmanager
async def lifespan(server: FastAPI):
    startup()
    yield
    shutdown()


def collect_papers():
    papers: list[ArxivPaper] = collect_arxiv_papers(
        search_query="cat:cs.*",
        id_list=None,
        max_results=10,
        start=0,
    )

    for paper in papers:
        requests.post()


# server = FastAPI(lifespan=lifespan)
