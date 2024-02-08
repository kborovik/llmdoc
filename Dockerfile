FROM python:3.11-slim as base

LABEL org.opencontainers.image.source="https://github.com/kborovik/llmdoc"
LABEL org.opencontainers.image.description="Generative AI (RAG) + ElasticSearch"
LABEL org.opencontainers.image.licenses="MIT"

ENV debian_frontend=noninteractive

RUN apt update -y && apt install -y curl

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

RUN python -m spacy download en_core_web_sm

FROM base as build

ARG VERSION

COPY llmdoc-${VERSION}-py3-none-any.whl /tmp/llmdoc-${VERSION}-py3-none-any.whl

RUN pip install --no-cache-dir /tmp/llmdoc-${VERSION}-py3-none-any.whl

ENTRYPOINT [ "uvicorn", "llmdoc.api_v1:app", "--interface=wsgi", "--host=0.0.0.0", "--no-access-log"]