from pydantic import BaseModel

class Topic(BaseModel):
    name: str
    concepts: list[str]

class PdfExtractionOutput(BaseModel):
    topics: list[Topic]
