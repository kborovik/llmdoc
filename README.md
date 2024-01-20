# Document Search Results Summarization with Large Language Model (LLM)

This project applies a Large Language Model (LLM) to summarize search results from ElasticSearch document queries.

# Demo

# Prerequisites

The deployment was tested on Ubuntu 22.04 (x86_64 architecture) and macOS 14 (Apple silicon/arm64 architecture). Although Windows Subsystem for Linux (WSL) could potentially support the deployment, compatibility in that environment was not verified firsthand.

## Docker

**Install Docker**

https://docs.docker.com/engine/install/

## For Linux

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

## For macOS

# Quick Start

- Clone GitHub repository
- Set ELASTIC_PASSWORD
- Initialize repository (setup Python and ElasticSearch environment)
- Start Docker Compose (ElasticSearch, Kibana, Ollama LLM Model)
- Run end-to-end test

```shell
git clone https://github.com/kborovik/llmdoc.git
cd llmdoc
export ELASTIC_PASSWORD=MyBigPass45
make init
make start
make test
```

# Configuration

Configuration settings can be specified either by exporting environment variables in the command prompt (terminal) or by creating a `.env` file. Configuration settings specified through environment variables or in the .env file are not case-sensitive. For example, `ELASTIC_PASSWORD` and `elastic_password` would be treated equivalently.

```shell
export ELASTIC_PASSWORD=MyBigPass45
```

```shell
cat .env
ELASTIC_PASSWORD=MyBigPass45
```

The full list of supported configuration settings can be found in the `llmdoc/config.py` file.
