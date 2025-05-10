import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from constants.concept_status import CREATED

class Concept(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    keyword: str
    topic: str

    status: str = Field(default=CREATED)

    kiddo_id: int = Field(foreign_key="kiddo.id")
    linked_to_id: Optional[int] = Field(default=None, foreign_key="concept.id")

    linked_concepts: List["Concept"] = Relationship(back_populates="linked_to")

    created_at: datetime = Field(default_factory=datetime.utcnow)