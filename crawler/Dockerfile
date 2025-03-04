FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /workspace

CMD ["uvicorn", "main:server", "--reload", "--host", "0.0.0.0", "--port", "8080"]