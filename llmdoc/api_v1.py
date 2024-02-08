import json
import sys

import falcon
from falcon import Request, Response
from loguru import logger

from . import cfg, elastic, es, llm

fmt = "<level>{level}</level>:     {message}"
logger.remove()
logger.add(sink=sys.stdout, level="INFO", format=fmt, enqueue=True)


class HealthCheck:
    """
    Health Check
    """

    def on_get(self, req: Request, resp: Response) -> None:
        resp.status = falcon.HTTP_200

    def on_head(self, req: Request, resp: Response) -> None:
        resp.status = falcon.HTTP_200


class Search:
    """
    Search
    """

    def on_post(self, req: Request, resp: Response) -> None:
        try:
            data = json.load(req.bounded_stream)
            logger.info(f"Request: {data}")
            result = llm.search(data)
            logger.info(f"Response: {result}")
            resp.media = result
            resp.status = falcon.HTTP_200
        except Exception as error:
            logger.exception(error)
            resp.media = {"error": str(error)}
            resp.status = falcon.HTTP_500


app = falcon.App()
app.req_options.strip_url_path_trailing_slash = True

health = HealthCheck()

app.add_route("/health", health)
