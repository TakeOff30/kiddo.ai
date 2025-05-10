from sqlmodel import select
from fastapi.db import AsyncSessionFactory
from fastapi.models.concept import Concept # Make sure Concept model is defined in fastapi/models/concept.py
from google.adk.tools import ToolContext

async def get_known_concepts(cxt: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has learned so far.
    """
    
    concepts_list = []
    async with AsyncSessionFactory() as session:
        query = select(Concept).where(Concept.status == "learned") # Assumes Concept has a 'status' field
        result = await session.execute(query)
        concepts_list = result.scalars().all()
    return concepts_list

async def retrieve_topic(cxt: ToolContext, topic: str) -> list:
    """
    This function retrieves from vectorial database the chunks of notes related to the topic
    """
    
    
    return related_concepts