import json
from api.adk.models.pdf_extraction_output import PdfExtractionOutput
from api.db import AsyncSessionFactory
from api.models.concept import Concept
from api.models.kiddo import Kiddo
from google.adk.tools import ToolContext
from sqlmodel import select


async def save_topic_on_db(topics: str):
    print("Saving topic on database...")

    kiddo_id = 1

    topic_concepts_list = PdfExtractionOutput(**json.loads(topics))

    concepts = []
    for topic in topic_concepts_list.topics:
        for concept in topic.concepts:
            concepts.append(Concept(text=concept, topic=topic.name, kiddo_id=kiddo_id))

    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
        kiddo = result.scalar_one()
        kiddo.topics = json.dumps([topic.name for topic in topic_concepts_list.topics])
        session.add_all(concepts)
        await session.commit()
        await session.refresh(kiddo)


