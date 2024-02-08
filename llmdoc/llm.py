from typing import Any, List, Mapping

import ollama
from loguru import logger

from . import cfg

url = f"http://{cfg.ollama_host}:{cfg.ollama_port}"

client = ollama.Client(host=url)


def pull(model: str = cfg.ollama_model) -> None:
    """
    Pull LLM Model
    """
    resp = client.list()
    models = [item["name"] for item in resp["models"]]

    if model not in models:
        logger.info("Pulling LLM model {}", model)
        try:
            client.pull(model=cfg.ollama_model)
        except Exception as error:
            logger.error(error)

        logger.success("Pulled LLM model {}", cfg.ollama_model)


def stream(prompt: str) -> None:
    """
    Stream LLM Prompt Response
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty or null.")

    stream = client.generate(
        model=cfg.ollama_model,
        prompt=prompt,
        stream=True,
        options=cfg.ollama_options,
    )

    try:
        for part in stream:
            print(part["response"], end="", flush=True)

            if part["done"]:
                print("\n")
                logger.opt(ansi=True).success(
                    "Prompt+Context size <yellow>{}</yellow> tokens. Response size <yellow>{}</yellow> tokens",
                    part.get("prompt_eval_count"),
                    part.get("eval_count"),
                )
    except Exception as error:
        logger.error("Host {}, {}", url, error)


def generate(prompt: str) -> Mapping[str, Any]:
    """
    Generate LLM Prompt Response
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty or null.")

    try:
        resp = client.generate(
            model=cfg.ollama_model,
            prompt=prompt,
            stream=False,
            options=cfg.ollama_options,
        )
    except Exception as error:
        logger.error("Host {}, {}", url, error)

    return {
        "eval_count": resp.get("eval_count"),
        "eval_duration": resp.get("eval_duration"),
        "prompt_eval_count": resp.get("prompt_eval_count"),
        "response": resp.get("response"),
    }


def embeddings(prompt: str) -> List[float]:
    """
    Generate LLM embeddings.
    """
    if not prompt:
        raise ValueError("Text cannot be empty or null.")

    logger.debug("Embeddings text: {}", repr(prompt))

    try:
        resp = ollama.embeddings(model=cfg.ollama_model, prompt=prompt)
    except Exception as error:
        logger.error("Host {}, {}", url, error)

    return resp["embedding"]
