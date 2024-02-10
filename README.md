# Document Question Answering with Generative AI and Elasticsearch

This project demonstrates a DevOps workflow for automating and functionally testing local development that integrates seamlessly with cloud DevOps workflows. It focuses on functional and integration testing with ElasticSearch and Ollama rather than unit testing. For details on the Terraform and Kubernetes deployment workflow, see the related project here: https://github.com/kborovik/llmdoc-infra

`llmdoc` Python application utilizes a Retrieval-Augmented Generation (RAG) approach, leveraging a Large Language Model (LLM), to condense search results obtained from ElasticSearch document queries into summaries.

The `llmdoc` project utilizes the [spaCy](https://spacy.io/) library to analyze text. It performs various tasks such as sentence splitting, generating sentence lemmas, grouping sentences and lemmas into chunks, generating embeddings using a Large Language Model, and storing the generated document in an ElasticSearch index.

# Quick Start

- Clone GitHub repository
- Set ELASTIC_PASSWORD
- Initialize local development environment (Docker Compose, ElasticSearch)
- Start Docker Compose (ElasticSearch, Kibana, Ollama LLM Model)
- Run end-to-end test

```shell
git clone https://github.com/kborovik/llmdoc.git
cd llmdoc
echo "ELASTIC_PASSWORD=MyBigPass45" > .env
make init status
make test
```

## Local Development Environment Setup

```shell
make init status
```

<a href="https://asciinema.org/a/637410" target="_blank"><img src="https://asciinema.org/a/637410.svg" /></a>

## Functional Tests

```shell
make test
```

<a href="https://asciinema.org/a/637413" target="_blank"><img src="https://asciinema.org/a/637413.svg" /></a>

## Search Query Debug

```shell
llmdoc search --query "Who is Count Von Kramm?" --debug
```

<a href="https://asciinema.org/a/637414" target="_blank"><img src="https://asciinema.org/a/637414.svg" /></a>

## Document Index Debug

```shell
llmdoc index --file tests/test.txt --debug
```

<a href="https://asciinema.org/a/637416" target="_blank"><img src="https://asciinema.org/a/637416.svg" /></a>


# Prerequisites

The deployment was tested on Ubuntu 22.04 (linux/amd64 architecture). Although Windows Subsystem for Linux (WSL) could potentially support the deployment, compatibility in that environment was not verified firsthand.

Install:

- **docker** https://docs.docker.com/engine/install
- **poetry** https://github.com/python-poetry/poetry

## NVIDIA GPU Support

**Install NVIDIA `apt` network repository for Ubuntu**

https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#network-repo-installation-for-ubuntu

**Install NVIDIA Linux drivers**

```
sudo apt install nvidia-headless-545
```

**Install NVIDIA Container Runtime for Docker**

```
sudo apt install nvidia-docker2
```

# Configuration

Configuration settings can be specified either by exporting environment variables in the command prompt (terminal) or by creating a `.env` file. Configuration settings specified through environment variables or in the .env file are not case-sensitive. For example, `ELASTIC_PASSWORD` and `elastic_password` would be treated equivalently.

```shell
export ELASTIC_PASSWORD=MyBigPass45
```

```shell
echo "ELASTIC_PASSWORD=MyBigPass45" >> .env
```

The full list of supported configuration settings can be found in the `llmdoc/config.py` file.

# Pipeline

## Document Intake

1. Split text into sentences with spaCy library
1. Lemmatize sentence with spaCy library
1. Group sentences into ElasticSearch documents
1. Generate embedding for KNN search with Large Language Model (LLM)
1. Store documents in ElasticSearch index

## Document Search

1. Generate embeddings for KNN search with LLM
2. Send combined BM25+KNN query to ElasticSearch
3. Construct LLM prompt with ElasticSearch query results
4. Steam (or JSON) LLM prediction
