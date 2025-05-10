from datetime import date
import json
from typing import List, Optional
from fastapi.models.concept import Concept
from sqlmodel import Field, SQLModel, Relationship


class Kiddo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exame_name: str
    exam_date: date
    studying_days: str
    img_url: Optional[str] = None

    concepts: List["Concept"] = Relationship(back_populates="kiddo")


    def get_studying_days(self) -> List[str]:
        return json.loads(self.studying_days)

    def set_studying_days(self, studying_days: List[str]):
        self.studying_days = json.dumps(studying_days)
