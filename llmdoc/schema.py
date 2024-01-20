from pydantic import BaseModel


class ElasticDoc(BaseModel):
    name: str
    text: str
    lemma: str
    embed: list[float]


class ElasticHits(BaseModel):
    id: str
    score: float
    text: str


class TextChunk(BaseModel):
    text: str
    lemma: str
