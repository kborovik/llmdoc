# Document Question Answering with Generative AI and Elasticsearch

**Project Overview**

This project provides a hands-on demonstration of a DevOps workflow designed to automate and test local development environments with seamless integration into cloud-based DevOps processes.  The focus lies on functional and integration testing specifically involving Elasticsearch and Ollama, rather than isolated unit testing. 

For the associated Terraform and Kubernetes deployment workflow, please refer to the companion project: [https://github.com/kborovik/llmdoc-infra](https://github.com/kborovik/llmdoc-infra)

**Core Technology**

The `llmdoc` Python application employs a Retrieval-Augmented Generation (RAG) approach. It leverages a Large Language Model (LLM) to summarize search results retrieved from Elasticsearch document queries.

**Key Dependencies**

* spaCy: [https://spacy.io/](https://spacy.io/) library for text analysis tasks.
* Elasticsearch for document indexing and search.
* Ollama (or similar) Large Language Model

**Workflow Summary**

1. **Text Analysis:** `llmdoc` uses spaCy to:
   * Break text into sentences.
   * Generate lemmas (base word forms).
   * Group related sentences and lemmas.
2. **Embedding Generation:** An LLM creates text embeddings (numerical representations).
3. **Elasticsearch Indexing:** Embeddings and associated text are stored in Elasticsearch.

**Quick Start Guide**

1. **Clone Repository:** Get the code from GitHub.
2. **Environment Setup:**
   * Set the `ELASTIC_PASSWORD` environment variable.
   * Initialize your local environment using Docker Compose (Elasticsearch included).
3. **Launch Containers:** Start Docker Compose (this runs Elasticsearch, Kibana, and the Ollama LLM).
4. **Run Tests:** Execute the end-to-end test suite.


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

[![asciicast](https://asciinema.org/a/637422.svg)](https://asciinema.org/a/637422)

## Functional Tests Pipeline

**Purpose:** This pipeline verifies the core functionality of the ``llmdoc``. 

**Tested Components and Functionality**

* **Build Processes**
    * Successful creation of a Python Wheel package.
    * Successful building of the Docker container image.
* **Docker Deployment**
    * Correct configuration of Docker Compose for deployment.
* **Search and Indexing**
    * Indexing of data into ElasticSearch using the `llmdoc` component.
    * Execution of valid ElasticSearch queries using `llmdoc`.
* **LLM (Large Language Model) Integration**
    * LLM's ability to comprehend a topic without external search results. 
    * LLM's capability to accurately interpret provided search results. 
* **API Interactions**
    * Correct functionality of the `llmdoc` REST API endpoints.

```shell
make test
```

[![asciicast](https://asciinema.org/a/637610.svg)](https://asciinema.org/a/637610)

## Search Query Debug

```shell
llmdoc search --query "Who is Count Von Kramm?" --debug
```

[![asciicast](https://asciinema.org/a/637419.svg)](https://asciinema.org/a/637419)

## Document Index Debug

```shell
llmdoc index --file tests/test.txt --debug
```

[![asciicast](https://asciinema.org/a/637420.svg)](https://asciinema.org/a/637420)


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
