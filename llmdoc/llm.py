import logging

import requests

from . import CFG

session = requests.Session()


def generate(prompt: str) -> str:
    """
    Generate LLM Prompt Response
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty or null.")

    ollama_generate_url = f"http://{CFG.ollama_host}:{CFG.ollama_port}/api/generate"

    ollama_generate_data = {
        "prompt": prompt,
        "model": CFG.ollama_model,
        "stream": False,
    }

    logging.info("Send query to Large Language Model")
    logging.debug(f"LLM Model: {CFG.ollama_model}")

    reply = session.post(url=ollama_generate_url, json=ollama_generate_data)

    reply.raise_for_status()

    json_data = reply.json()

    total_duration = float(json_data.get("total_duration", 0.0)) / 10**9
    context_tokens = len(json_data.get("context", ""))
    generated_tokens = json_data.get("eval_count", 0)

    logging.info(
        f"Total time: {total_duration:.2f}s, Context tokens: {context_tokens}, Generated tokens: {generated_tokens}"
    )

    return json_data["response"]


def embeddings(text: str) -> list[float]:
    """
    Generate LLM embeddings using an external API.
    """
    if not text:
        raise ValueError("Text cannot be empty or null.")

    ollama_embeddings_url = f"http://{CFG.ollama_host}:{CFG.ollama_port}/api/embeddings"

    ollama_embeddings_data = {
        "prompt": text,
        "model": CFG.ollama_model,
    }

    logging.info("Generate embeddings")
    logging.debug(f"Embedding text: {repr(text)}")

    reply = session.post(url=ollama_embeddings_url, json=ollama_embeddings_data)

    reply.raise_for_status()

    return reply.json()["embedding"]
