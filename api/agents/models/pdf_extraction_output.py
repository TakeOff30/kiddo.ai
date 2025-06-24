from typing import List
from pydantic import BaseModel

class Topic(BaseModel):
    topic: str
    concepts: List[str]

class PdfExtractionOutput(BaseModel):
    topics: List[Topic]
