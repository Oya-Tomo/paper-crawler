FROM ubuntu:24.04

WORKDIR /workspace

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

RUN python3 -m venv /venv

RUN /venv/bin/python3 -m pip install \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    requests \
    sqlalchemy \
    psycopg2-binary

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"