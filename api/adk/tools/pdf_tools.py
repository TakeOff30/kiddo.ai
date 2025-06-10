from api.db import AsyncSessionFactory
from api.models.kiddo import Kiddo
from google.adk.tools import ToolContext
from sqlmodel import select


async def save_topic_on_db(topic: str):
    print("Saving topic on database...")

    kiddo_id = ToolContext.state["kiddo_id"]
    async with AsyncSessionFactory() as session:
        kiddo = await session.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
        kiddo.topic = topic
        await session.commit()
        await session.refresh(kiddo)

   