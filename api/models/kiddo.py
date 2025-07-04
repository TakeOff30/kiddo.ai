from datetime import date
import json
from typing import TYPE_CHECKING, Any, List, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from api.models.concept import Concept

class Kiddo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exame_name: str
    exam_date: date
    studying_days: str
    img_url: Optional[str] = None
    topics: Optional[str] = None

    concepts: List["Concept"] = Relationship(back_populates="kiddo")

    def get_studying_days(self) -> List[str]:
        return json.loads(self.studying_days)

    def set_studying_days(self, studying_days: List[str]):
        self.studying_days = json.dumps(studying_days)

    def get_topics(self) -> List[dict[str, Any]]:
        return json.loads(self.topics)

    def set_get_topics(self, topics: List[dict[str, Any]]):
        self.topics = json.dumps(topics)
