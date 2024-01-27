import sys

from elasticsearch import Elasticsearch
from loguru import logger

from .config import Config
from .schema import ElasticDoc, ElasticHits, TextChunk

logger.remove()
logger.level("DEBUG", color="<blue>")
logger.level("INFO", color="<white>")
logger.level("SUCCESS", color="<green>")
logger.level("ERROR", color="<red>")
logger.add(sink=sys.stdout, level="INFO", enqueue=True)

try:
    cfg = Config()
except ValueError as e:
    logger.error(e)
    sys.exit(1)

es = Elasticsearch(
    hosts=f"https://{cfg.elastic_host}:{cfg.elastic_port}",
    basic_auth=(cfg.elastic_user, cfg.elastic_password.get_secret_value()),
    ca_certs=cfg.elastic_ca_certs,
)

__all__ = ["cfg", "es", "ElasticDoc", "ElasticHits", "TextChunk"]
