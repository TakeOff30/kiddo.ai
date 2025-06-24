from api.adk.models.pdf_extraction_output import PdfExtractionOutput
from api.db import AsyncSessionFactory
from api.models.kiddo import Kiddo
from google.adk.tools import ToolContext
from sqlmodel import select


async def save_topic_on_db(topics: str):
    print("Saving topic on database...")

    kiddo_id = 1
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
        kiddo = result.scalar_one()
        kiddo.topics = topics
        await session.commit()
        await session.refresh(kiddo)
