from typing import List

from elasticsearch.exceptions import BadRequestError
from loguru import logger

from . import ElasticDoc, ElasticHits, TextChunk, cfg, es, llm

elastic_mappings = {
    "properties": {
        "name": {
            "type": "text",
        },
        "text": {
            "type": "text",
        },
        "lemma": {
            "type": "text",
        },
        "embed": {
            "type": "dense_vector",
            "dims": cfg.embed_dims,
            "index": "true",
            "similarity": "cosine",
        },
    }
}


def init() -> None:
    """
    Initialize Elastic Storage (Index)
    """
    try:
        es.indices.create(
            index=cfg.elastic_index_name, mappings=elastic_mappings
        )
    except BadRequestError as error:
        if error.error == "resource_already_exists_exception":
            pass
        else:
            logger.error(error.body)
            raise


def index(chunks: List[TextChunk], doc_id: str) -> None:
    """
    Elastic Index NLP Document
    """
    if not chunks:
        return

    if not doc_id:
        raise ValueError("doc_id is required")

    for i, chunk in enumerate(chunks):
        elastic_doc = ElasticDoc(
            name=f"{doc_id}-{i}",
            text=chunk.text,
            lemma=chunk.lemma,
            embed=llm.embeddings(prompt=chunk.lemma),
        )
        es.index(
            id=f"{doc_id}-{i}",
            index=cfg.elastic_index_name,
            document=elastic_doc.model_dump(),
        )
        logger.success("Indexed {}", f"{doc_id}-{i}")

        logger.opt(ansi=True).debug(
            "\n<yellow>Text:</yellow>\n{}\n<yellow>Lemma:</yellow>\n{}\n",
            repr(chunk.text),
            repr(chunk.lemma),
        )


def search(query: str) -> list[ElasticHits]:
    """
    Elastic BM25 + KNN search
    """

    bm25 = {
        "match": {
            "text": {
                "query": query,
                "boost": cfg.elastic_bm25_boost,
            },
        },
    }

    knn = {
        "field": "embed",
        "query_vector": llm.embeddings(prompt=query),
        "k": cfg.elastic_search_size * 2,
        "num_candidates": 10000,
        "boost": cfg.elastic_knn_boost,
    }

    reply = es.search(
        index=cfg.elastic_index_name,
        fields=["text"],
        size=cfg.elastic_search_size,
        query=bm25,
        knn=knn,
    )

    hits = reply["hits"]["hits"]
    docs = []

    for hit in hits:
        if hit["_score"] > cfg.elastic_search_score:
            docs.append(
                ElasticHits(
                    id=hit["_id"],
                    score=hit["_score"],
                    text=hit["_source"]["text"],
                )
            )

    return docs
