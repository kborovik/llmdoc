import json
import sys
from pathlib import Path

from loguru import logger
from typer import Option, Typer

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
        logger.info("Deleting Elastic Index {}", cfg.elastic_index_name)
        try:
            response = es.indices.delete(index=cfg.elastic_index_name)
        except NotFoundError:
            logger.info("Elastic Index not found")
        logger.success("Deleted Elastic Index {}", cfg.elastic_index_name)
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
    file: str = Option(help="File", exists=True, dir_okay=False),
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

    file = Path(file).resolve()
    if not file.is_file():
        logger.error("{} is not a file", file)
        sys.exit(1)

    logger.info("Reading file {}", file)
    text = file.read_text(encoding="utf-8")

    doc_id = file.name

    nlp_doc = nlp.analyze(text=text)

    logger.info("Splitting {} into sentence groups", doc_id)
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
    logger.success("Splitted into {} sentence groups", len(chunks))

    logger.info("Indexing file {}", doc_id)
    elastic.init()
    elastic.index(chunks=chunks, doc_id=doc_id)


@cli.command(no_args_is_help=True)
def search(
    query: str = Option(help="Search query"),
    search_score: float = Option(
        help=f"Search score filter (current settings: {cfg.elastic_search_score})",
        default=None,
    ),
    search_size: int = Option(
        help=f"Number of search hits (current settings: {cfg.elastic_search_size})",
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
        cfg.elastic_search_score = search_score

    if search_size:
        cfg.elastic_search_size = search_size

    if elastic_index_name:
        cfg.elastic_index_name = elastic_index_name

    logger.info("Search query: {}", query)

    try:
        resp = elastic.search(query=query)
    except Exception as error:
        logger.error(error)
        sys.exit(1)

    if len(resp) == 0:
        logger.warning(
            "No results found, decrease `search-score` below {}",
            cfg.elastic_search_score,
        )
        sys.exit(0)

    context = ""
    for doc in resp:
        logger.opt(ansi=True).debug(
            "\n<yellow>ID: {}\nScore: {}</yellow>\n{}\n",
            doc.id,
            doc.score,
            doc.text,
        )
        context += f"\n{doc.text}\n"

    logger.success("Found {} results", len(resp))

    prompt = f"Answer user question based on the search results.\nUser question: {query}.\nSearch results:\n{context}\n"

    llm.stream(prompt=prompt)


@cli.command(no_args_is_help=True)
def generate(
    prompt: str = Option(help="LLM Prompt"),
    stream: bool = Option(help="Stream response", default=True),
) -> None:
    """
    Query LLM without search context
    """
    from . import llm

    if stream:
        llm.stream(prompt=prompt)
    else:
        repl = llm.generate(prompt=prompt)
        print(json.dumps(repl))


@cli.command(no_args_is_help=True)
def embeddings(
    text: str = Option(help="Embeddings text"),
):
    """
    Generate LLM embeddings
    """
    from . import llm

    try:
        resp = llm.embeddings(prompt=text)
    except Exception as error:
        logger.error(error)
        sys.exit(1)

    print(resp)


@cli.command(no_args_is_help=False)
def model(
    name: str = Option(help="Ollama model name", default=cfg.ollama_model),
):
    """
    Pull Ollama LLM model
    """
    from . import llm

    try:
        llm.pull(model=name)
    except Exception as error:
        logger.error(error)
        sys.exit(1)
