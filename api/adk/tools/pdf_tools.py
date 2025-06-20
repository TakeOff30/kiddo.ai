from api.db import AsyncSessionFactory
from api.models.kiddo import Kiddo
from google.adk.tools import ToolContext
from sqlmodel import select


async def save_topic_on_db(topics: str):
    print("Saving topic on database...")

    # TODO: make the agent return without the `json` prefix
    cleaned_topics = clean_topics(topics)

    kiddo_id = 1
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
        kiddo = result.scalar_one()
        kiddo.topics = cleaned_topics
        await session.commit()
        await session.refresh(kiddo)

   
def clean_topics(topics: str) -> str:
    cleaned = topics.strip('`')
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]
    
    return cleaned