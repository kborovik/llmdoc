import json
import logging
from pathlib import Path

from typer import Exit, Option, Typer

from . import CFG, ES

app = Typer(name="llmdocs", no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.callback()
def callback():
    """
    Document Query with Large Language Model (LLM)
    """


@app.command()
def config():
    """
    Show config
    """
    print(CFG.model_dump_json())


@app.command(no_args_is_help=True)
def storage(
    create: bool = Option(help="Create index", default=None),
    delete: bool = Option(help="Delete index", default=None),
    show: bool = Option(help="Show info", default=None),
    stats: bool = Option(help="Show stats", default=None),
    debug: bool = Option(help="Enable debug", default=None),
):
    """
    Manage storage
    """
    from elasticsearch.exceptions import NotFoundError

    from . import elastic

    if debug:
        logging.getLogger().setLevel(level="DEBUG")

    if delete:
        try:
            response = ES.indices.delete(index=CFG.elastic_index_name)
        except NotFoundError:
            logging.info("Elastic Index not found")
    elif stats:
        try:
            response = ES.indices.stats(index=CFG.elastic_index_name)
            print(json.dumps(response.body["indices"]))
        except NotFoundError:
            logging.info("Elastic Index not found")
    elif show:
        try:
            response = ES.indices.get(index=CFG.elastic_index_name)
            print(json.dumps(response.body))
        except NotFoundError:
            logging.info("Elastic Index not found")
    elif create:
        elastic.init()


@app.command(no_args_is_help=True)
def index(
    file: Path = Option(help="File", resolve_path=True),
    elastic_index_name: str = Option(
        help=f"Elastic Index Name (current settings: {CFG.elastic_index_name})",
        default=None,
    ),
    debug: bool = Option(help="Enable debug", default=None),
) -> None:
    """
    Index document
    """
    from . import elastic, nlp

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if elastic_index_name:
        CFG.elastic_index_name = elastic_index_name

    if not file.is_file():
        logging.error(f"INDEX -  {file} is not a file")
        raise Exit(1)

    logging.info(f"INDEX -  Read file {file}")
    text = file.read_text(encoding="utf-8")

    doc_id = file.name

    logging.info(f"INDEX - Analyzing {doc_id}")
    nlp_doc = nlp.analyze(text=text)

    logging.info(f"INDEX - Splitting {doc_id} into chunks")
    chunks = nlp.chunk(
        doc=nlp_doc,
        chunk_size=CFG.chunk_words,
    )
    logging.info(f"INDEX - Generated {len(chunks)} chunks")

    logging.debug(
        f"INDEX - First Chunk\n==> Text <==\n{repr(chunks[0].text)}\n==> Lemma <==\n{repr(chunks[0].lemma)}\n"
    )
    logging.debug(
        f"INDEX - Last Chunk\n==> Text <==\n{repr(chunks[-1].text)}\n==> Lemma <==\n{repr(chunks[-1].lemma)}\n"
    )

    logging.info(f"INDEX - Indexing file: {doc_id}")

    elastic.init()
    elastic.index(chunks=chunks, doc_id=doc_id)


@app.command(no_args_is_help=True)
def search(
    query: str = Option(help="Search query"),
    debug: bool = Option(help="Enable debug", default=None),
    search_score: float = Option(
        help=f"Search score filter (current settings: {CFG.search_score})", default=None
    ),
    search_size: int = Option(
        help=f"Number of search hits (current settings: {CFG.search_size},)",
        default=None,
    ),
    elastic_index_name: str = Option(
        help=f"Elastic Index Name (current settings: {CFG.elastic_index_name})",
        default=None,
    ),
) -> None:
    """
    Search documents and generate LLM response
    """
    from . import elastic, llm

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if search_score:
        CFG.search_score = search_score

    if search_size:
        CFG.search_size = search_size

    if elastic_index_name:
        CFG.elastic_index_name = elastic_index_name

    reply = elastic.search(query=query)

    if len(reply) == 0:
        logging.info(
            f"SEARCH - No results found, decrease `search-score` below {CFG.search_score}"
        )
        raise Exit(0)

    context = ""
    for doc in reply:
        logging.info(f"\nID: {doc.id}\nScore: {doc.score}\n{doc.text}\n")
        context += f"document-id {doc.id}\n{doc.text}\n\n"

    prompt = f"""
        User question: \n{query}\n
        Search results: \n{context}\n
        """

    reply = llm.generate(prompt=prompt)

    print(f"\n{reply}")


@app.command(no_args_is_help=True)
def generate(
    text: str = Option(help="LLM Prompt"),
    debug: bool = Option(help="Enable debug", default=None),
) -> None:
    """
    Query LLM without search context
    """

    from . import llm

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    reply = llm.generate(prompt=text)

    print(reply)


@app.command(no_args_is_help=True)
def embeddings(
    text: str = Option(help="Content"),
    debug: bool = Option(help="Enable debug", default=None),
):
    """
    Generate LLM embeddings
    """

    from . import llm

    if debug:
        logging.getLogger().setLevel(level="DEBUG")

    reply = llm.embeddings(text=text)

    print(reply)
