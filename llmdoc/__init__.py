import logging
from os import getenv

from elasticsearch import Elasticsearch

from .config import Config
from .schema import ElasticDoc, ElasticHits, TextChunk

logging.basicConfig(
    level=getenv("LOGLEVEL"),
    format="[%(relativeCreated)5dms %(levelname)s] (%(module)s.%(funcName)s) %(message)s",
)


try:
    cfg = Config()
except ValueError as e:
    logging.error(e.errors())
    exit(1)

es = Elasticsearch(
    hosts=f"https://{cfg.elastic_host}:{cfg.elastic_port}",
    basic_auth=(cfg.elastic_user, cfg.elastic_password.get_secret_value()),
    ca_certs=cfg.elastic_ca_certs,
)

__all__ = ["cfg", "es", "ElasticDoc", "ElasticHits", "TextChunk"]
