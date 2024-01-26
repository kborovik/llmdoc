from pydantic import BaseModel


class TextChunk(BaseModel):
    text: str
    lemma: str


class ElasticDoc(TextChunk):
    name: str
    embed: list[float]


class ElasticHits(BaseModel):
    id: str
    score: float
    text: str
