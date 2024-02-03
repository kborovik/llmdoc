from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration"""

    chunk_words: int = 300
    search_size: int = 3
    search_score: float = 2.5
    embed_dims: int = 4096

    elastic_ca_certs: str = "certs/ca.crt"
    elastic_host: str = "localhost"
    elastic_port: int = 9200
    elastic_index_name: str = "llmdoc"
    elastic_password: SecretStr = None
    elastic_user: str = "elastic"

    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "mistral:latest"
    ollama_options: dict = {
        "temperature": 0.8,  # The temperature of the model.
        "num_ctx": 4096,  # Sets the size of the context window used to generate the next token
        "num_predict": 125,  # Maximum number of tokens to predict when generating text
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        str_strip_whitespace=True,
        frozen=False,
    )
