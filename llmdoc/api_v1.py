import falcon
from falcon import Request, Response
from loguru import logger

from . import cfg, elastic, es, llm


class HealthCheck:
    """
    Health Check
    """

    def on_get(self, req: Request, resp: Response) -> None:
        try:
            es.info()
            resp.media = {"elastic_host": cfg.elastic_host}
            resp.status = falcon.HTTP_200
        except Exception as error:
            logger.error(error)
            resp.media = {"error": str(error)}
            resp.status = falcon.HTTP_503


class Search:
    """
    Search
    """

    def on_post(self, req: Request, resp: Response) -> None:
        try:
            obj = req.get_media()
        except Exception as error:
            logger.exception(error)
            resp.media = {"error": str(error)}
            resp.status = falcon.HTTP_500

        query = obj["query"]
        context = ""
        search = []

        try:
            logger.info("Search query: {}", query)
            search_resp = elastic.search(query=query)
            logger.success("Found {} results", len(search_resp))
        except Exception as error:
            logger.error(error)

        for doc in search_resp:
            context += doc.text
            search.append({"id": doc.id, "score": doc.score, "text": doc.text})

        prompt = f"USER-QUESTION: {query}.\nSEARCH-RESULTS:\n\n{context}\n"

        try:
            logger.info("Generating LLM response")
            prediction = llm.generate(prompt=prompt)
            logger.success(
                "LLM Evaluation time {:.2f} sec.",
                prediction.get("eval_duration") / 1_000_000_000,
            )
        except Exception as error:
            logger.error(error)

        resp.media = {
            "model": cfg.ollama_model,
            "system": cfg.ollama_system,
            "query": query,
            "prediction": prediction.get("response"),
            "eval_duration": prediction.get("eval_duration"),
        }


app = falcon.App()
app.req_options.strip_url_path_trailing_slash = True

health = HealthCheck()
search = Search()

app.add_route("/health", health)
app.add_route("/search", search)
