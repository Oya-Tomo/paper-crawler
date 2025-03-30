import datetime
import pprint
from contextlib import asynccontextmanager

import apscheduler.schedulers
import apscheduler.schedulers.background
import apscheduler.util
import requests
from fastapi import FastAPI
import apscheduler

from env import SUMMARIZER_URL, COLLECTION_PERIOD
from arxiv.collector import collect_arxiv_papers, ArxivPaper


def startup():
    print("Starting up the server...")

    # Starting a periodic task to collect papers
    scheduler = apscheduler.schedulers.background.BackgroundScheduler()
    scheduler.add_job(
        collect_papers,
        "interval",
        seconds=60 * 60 * COLLECTION_PERIOD,  # Defined in docker-compose
        next_run_time=apscheduler.util.datetime.now()
        + apscheduler.util.timedelta(seconds=5),
    )
    scheduler.start()

    print("Scheduler started.")


def shutdown():
    print("Shutting down the server...")


@asynccontextmanager
async def lifespan(server: FastAPI):
    startup()
    yield
    shutdown()


def collect_papers():
    print(f"{datetime.datetime.now()} Collecting papers...")
    papers: list[ArxivPaper] = collect_arxiv_papers(
        search_query="all:LLM",
        id_list=None,
        max_results=10,
        start=0,
    )

    for paper in papers:
        print(f"Paper Primary Key: {paper.id} {paper.src}")
        result = requests.get(
            f"{SUMMARIZER_URL}/get",
            json={
                "id": paper.id,
                "src": paper.src,
            },
        )
        if result.status_code == 200 and result.json()["status"] == "ok":
            print(f"Paper already exists")
            print(f"Updating paper ...")

            result = requests.put(
                f"{SUMMARIZER_URL}/update",
                data=paper.model_dump_json(),
            )
            if result.status_code == 200:
                print(f"Updated paper: {result.status_code}")
                pprint.pprint(result.json())
            else:
                print(f"Failed to update paper: {result.status_code}")
                pprint.pprint(result.json())
                continue

        else:
            print("Create paper:")
            print(paper.model_dump_json(indent=2))
            result = requests.post(
                f"{SUMMARIZER_URL}/create",
                data=paper.model_dump_json(),
            )
            if result.status_code == 200:
                print(f"Created paper: {result.status_code}")
                pprint.pprint(result.json())
            else:
                print(f"Failed to create paper: {result.status_code}")
                pprint.pprint(result.json())
                continue

        print("Executing summarization...")
        result = requests.post(
            f"{SUMMARIZER_URL}/summarize",
            json={
                "id": paper.id,
                "src": paper.src,
            },
        )
        if result.status_code == 200:
            print(f"Being summarized ...")
            pprint.pprint(result.json())


server = FastAPI(lifespan=lifespan)
