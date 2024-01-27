import json
import sys
from pathlib import Path

from loguru import logger
from typer import Exit, Option, Typer

from . import cfg, es

cli = Typer(
    name="llmdocs", no_args_is_help=True, pretty_exceptions_show_locals=False
)


@cli.callback()
def callback():
    """
    Document Query with Large Language Model (LLM)
    """


@cli.command()
def config():
    """
    Show config
    """
    print(cfg.model_dump_json())


@cli.command(no_args_is_help=True)
def storage(
    create: bool = Option(help="Create index", default=None),
    delete: bool = Option(help="Delete index", default=None),
    show: bool = Option(help="Show info", default=None),
    stats: bool = Option(help="Show stats", default=None),
):
    """
    Manage storage
    """
    from elasticsearch.exceptions import NotFoundError

    from . import elastic

    if delete:
        try:
            response = es.indices.delete(index=cfg.elastic_index_name)
        except NotFoundError:
            logger.info("Elastic Index not found")
    elif stats:
        try:
            response = es.indices.stats(index=cfg.elastic_index_name)
            print(json.dumps(response.body["indices"]))
        except NotFoundError:
            logger.info("Elastic Index not found")
    elif show:
        try:
            response = es.indices.get(index=cfg.elastic_index_name)
            print(json.dumps(response.body))
        except NotFoundError:
            logger.info("Elastic Index not found")
    elif create:
        elastic.init()


@cli.command(no_args_is_help=True)
def index(
    file: Path = Option(help="File", default=None),
    elastic_index_name: str = Option(
        help=f"Elastic Index Name (current settings: {cfg.elastic_index_name})",
        default=None,
    ),
    debug: bool = Option(help="Debug", default=False),
) -> None:
    """
    Index document
    """
    from . import elastic, nlp

    if debug:
        logger.remove()
        logger.add(sink=sys.stdout, level="DEBUG", enqueue=True)

    if elastic_index_name:
        cfg.elastic_index_name = elastic_index_name

    if not file.is_file():
        logger.error("{} is not a file", file)
        raise Exit(1)

    logger.info("Reading file {}", file)
    text = file.read_text(encoding="utf-8")
    logger.success("Read file {}", file)

    doc_id = file.name

    logger.info("NLP Analyzing {}", doc_id)
    nlp_doc = nlp.analyze(text=text)
    logger.success("NLP Analyzed {}", doc_id)

    logger.info("Splitting {} into sentences chunks", doc_id)
    chunks = nlp.chunk(
        doc=nlp_doc,
        chunk_size=cfg.chunk_words,
    )
    logger.debug(
        "First Chunk\n==> Text <==\n{}\n==> Lemma <==\n{}\n",
        repr(chunks[0].text),
        repr(chunks[0].lemma),
    )
    logger.debug(
        "Last Chunk\n==> Text <==\n{}\n==> Lemma <==\n{}\n",
        repr(chunks[-1].text),
        repr(chunks[-1].lemma),
    )
    logger.success("Splitted into {} sentences chunks", len(chunks))

    logger.info("Indexing file: {}", doc_id)
    elastic.init()
    elastic.index(chunks=chunks, doc_id=doc_id)
    logger.success("Indexed file: {}", doc_id)


@cli.command(no_args_is_help=True)
def search(
    query: str = Option(help="Search query"),
    search_score: float = Option(
        help=f"Search score filter (current settings: {cfg.search_score})",
        default=None,
    ),
    search_size: int = Option(
        help=f"Number of search hits (current settings: {cfg.search_size},)",
        default=None,
    ),
    elastic_index_name: str = Option(
        help=f"Elastic Index Name (current settings: {cfg.elastic_index_name})",
        default=None,
    ),
    debug: bool = Option(help="Debug", default=False),
) -> None:
    """
    Search documents and generate LLM response
    """
    from . import elastic, llm

    if debug:
        logger.remove()
        logger.add(sink=sys.stdout, level="DEBUG", enqueue=True)

    if search_score:
        cfg.search_score = search_score

    if search_size:
        cfg.search_size = search_size

    if elastic_index_name:
        cfg.elastic_index_name = elastic_index_name

    logger.info("Search Query: {}", query)
    reply = elastic.search(query=query)
    if len(reply) == 0:
        logger.info(
            "No results found, decrease `search-score` below {}",
            cfg.search_score,
        )
        raise Exit(0)

    context = ""
    for doc in reply:
        logger.debug("\nID: {}\nScore: {}\n{}\n", doc.id, doc.score, doc.text)
        context += f"document-id {doc.id}\n{doc.text}\n\n"

    logger.success("Found {} results", len(reply))

    prompt = f"""
        User question: \n{query}\n
        Search results: \n{context}\n
        """

    logger.info("Generating LLM response")
    reply = llm.generate(prompt=prompt)

    print(f"\n{reply}")


@cli.command(no_args_is_help=True)
def generate(
    text: str = Option(help="LLM Prompt"),
) -> None:
    """
    Query LLM without search context
    """

    from . import llm

    reply = llm.generate(prompt=text)

    print(reply)


@cli.command(no_args_is_help=True)
def embeddings(
    text: str = Option(help="Content"),
):
    """
    Generate LLM embeddings
    """

    from . import llm

    reply = llm.embeddings(text=text)

    print(reply)
