from typing import Literal

from pydantic import FilePath, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration"""

    loglevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    chunk_words: int = 300
    embed_dims: int = 4096

    elastic_ca_certs: FilePath = "certs/ca.crt"
    elastic_host: str = "localhost"
    elastic_port: int = 9200
    elastic_index_name: str = "llmdoc"
    elastic_password: SecretStr = None
    elastic_user: str = "elastic"
    elastic_search_size: int = 5
    elastic_search_score: float = 3.0
    elastic_bm25_boost: float = 1.0
    elastic_knn_boost: float = 1.2

    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "llama3:instruct"
    ollama_system: str = "You are document question answering assistant. Answer USER-QUESTION based on SEARCH-RESULTS."
    ollama_options: dict = {
        "temperature": 0.2,  # LLM model temperature
        "num_ctx": 8192,  # LLM context length
        "num_predict": 1024,  # LLM output length
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        str_strip_whitespace=True,
        frozen=False,
    )
