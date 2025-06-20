from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, SQLModel, Relationship
from api.constants.concept_status import CREATED

if TYPE_CHECKING:
    from api.models.kiddo import Kiddo

class Concept(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    keyword: str
    topic: str

    status: str = Field(default=CREATED)

    kiddo_id: int = Field(foreign_key="kiddo.id")
    kiddo: Optional["Kiddo"] = Relationship(back_populates="concepts")
    
    linked_to_id: Optional[int] = Field(default=None, foreign_key="concept.id")
    linked_to: Optional["Concept"] = Relationship(back_populates="linked_concepts", sa_relationship_kwargs={"remote_side": "Concept.id"})

    linked_concepts: List["Concept"] = Relationship(back_populates="linked_to")

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))