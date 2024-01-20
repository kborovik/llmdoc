import re

import spacy
from spacy.tokens import Doc

from . import TextChunk

nlp = spacy.load("en_core_web_sm")


def analyze(text: str) -> Doc:
    """
    Analyze text with NLP

    Args:
        text (str): The text to be analyzed.

    Returns:
        Doc: The analyzed document as spacy.tokens.Doc.
    """
    text = re.sub(r"[\n\t]+", " ", text)

    return nlp(text)


def chunk(
    doc: Doc,
    chunk_size: int = 300,
) -> list[TextChunk]:
    """
    Group text into word chunks

    Parameters:
        doc (Doc): The input spaCy Doc object containing the text to be chunked.
        chunk_size (int, optional): The size of each chunk in number of words. Defaults to 300.

    Returns:
        list[TextChunk]: A list of TextChunk objects representing a group of sentences approximately chunk_size words in total.
    """
    size = len(doc)
    chunks = []

    for start in range(0, size, chunk_size):
        end = min(start + chunk_size, size)
        sent_start = doc[start].sent.start
        sent_end = doc[end - 1].sent.end
        batch = doc[sent_start:sent_end]
        words = [token.text_with_ws for token in batch]
        lemma = [
            token.lemma_
            for token in batch
            if not (
                token.is_punct or token.is_bracket or token.is_digit or token.is_stop
            )
        ]
        chunks.append(
            TextChunk(
                text="".join(words),
                lemma=" ".join(lemma),
            )
        )

    return chunks
