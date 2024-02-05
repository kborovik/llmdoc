import json
import sys

import falcon
from falcon import Request, Response
from loguru import logger

from . import cfg, elastic, es, llm

fmt = "<level>{level}</level>:     {message}"
logger.remove()
logger.level("INFO", color="<green>")
logger.add(sink=sys.stdout, level="INFO", format=fmt, enqueue=True)


class HealthCheck:
    """
    Health Check
    """

    def on_get(self, req: Request, resp: Response) -> None:
        resp.status = falcon.HTTP_200

    def on_head(self, req: Request, resp: Response) -> None:
        resp.status = falcon.HTTP_200


app = falcon.App()

health = HealthCheck()

app.add_route("/health", health)
