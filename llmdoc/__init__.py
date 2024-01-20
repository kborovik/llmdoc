import logging
from os import getenv

from elasticsearch import Elasticsearch

from .config import Config
from .schema import ElasticDoc, ElasticHits, TextChunk

logging.basicConfig(
    level=getenv("LOGLEVEL", default=logging.INFO),
    format="[%(relativeCreated)5dms %(levelname)s] (%(module)s.%(funcName)s) - %(message)s",
)


try:
    CFG = Config()
except ValueError as e:
    logging.error(e.errors())
    exit(1)

ES = Elasticsearch(
    hosts=f"https://{CFG.elastic_host}:{CFG.elastic_port}",
    basic_auth=(CFG.elastic_user, CFG.elastic_password.get_secret_value()),
    ca_certs=CFG.elastic_ca_certs,
)

__all__ = ["CFG", "ES", "ElasticDoc", "ElasticHits", "TextChunk"]
