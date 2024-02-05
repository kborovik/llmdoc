FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/kborovik/llmdoc"
LABEL org.opencontainers.image.description="Generative AI (RAG) + ElasticSearch"
LABEL org.opencontainers.image.licenses="MIT"

ARG VERSION

ENV debian_frontend=noninteractive

RUN apt update -y && apt install -y curl

COPY llmdoc-${VERSION}-py3-none-any.whl /tmp/llmdoc-${VERSION}-py3-none-any.whl

RUN pip install --no-cache-dir --upgrade /tmp/llmdoc-${VERSION}-py3-none-any.whl

RUN python -m spacy download en_core_web_sm

ENTRYPOINT [ "uvicorn", "llmdoc.api_v1:app", "--interface=wsgi", "--host=0.0.0.0", "--no-access-log"]