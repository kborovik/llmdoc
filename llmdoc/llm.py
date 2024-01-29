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

    stream = client.generate(model=cfg.ollama_model, prompt=prompt, stream=True)

    logger.info("Streaming LLM response")

    try:
        for part in stream:
            print(part["response"], end="", flush=True)
    except Exception as error:
        logger.error("Host {}, {}", url, error)


def generate(prompt: str) -> str:
    """
    Generate LLM Prompt Response
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty or null.")

    logger.info("Generating LLM response")

    try:
        resp = client.generate(
            model=cfg.ollama_model, prompt=prompt, stream=False
        )
    except Exception as error:
        logger.error("Host {}, {}", url, error)

    return resp["response"]


def embeddings(prompt: str) -> list[float]:
    """
    Generate LLM embeddings using an external API.
    """
    if not prompt:
        raise ValueError("Text cannot be empty or null.")

    logger.debug("Embeddings text: {}", repr(prompt))

    try:
        resp = ollama.embeddings(model=cfg.ollama_model, prompt=prompt)
    except Exception as error:
        logger.error("Host {}, {}", url, error)

    return resp["embedding"]
