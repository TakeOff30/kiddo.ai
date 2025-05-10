from fastapi.constants.concept_status import LEARNED, WRONG
from fastapi.services.vector_db_service import query_notes
from sqlmodel import select
from fastapi.db import AsyncSessionFactory
from fastapi.services.vector_db_service import query_notes
from sqlmodel import select
from fastapi.models.concept import Concept # Make sure Concept model is defined in fastapi/models/concept.py
from fastapi.constants.concept_status import LEARNED, WRONG
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool


async def get_known_concepts(cxt: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has learned so far.
    """
    
    concepts_list = []
    async with AsyncSessionFactory() as session:
        query = select(Concept).where(Concept.status == "learned")
        result = await session.execute(query)
        concepts_list = result.scalars().all()

    return concepts_list

async def get_unknown_concepts(cxt: ToolContext) -> str:
    """
    This function retrieves from the database a list of concepts that the Kiddo has not learned yet
    """
    kiddo_id = cxt.state["kiddo_id"]
    async with AsyncSessionFactory() as session:
        kiddo = select(Kiddo).where(Kiddo.id == kiddo_id)
        topics = kiddo.get_topics()
        list_of_topics = [topic["concepts"] for topic in topics]
    concepts_list = []
    async with AsyncSessionFactory() as session:
        query = select(Concept).where(Concept.kiddo_id == kiddo_id)
        result = await session.execute(query)
        concepts_list = result.scalars().all()
    
    unknown_concepts = [concept for concept in concepts_list if concept not in list_of_topics]
    
    return unknown_concepts


async def retrieve_topic(cxt: ToolContext, topic: str,  kiddo_id: int) -> list:
    """
    This function retrieves from vectorial database the chunks of notes related to the topic
    """
    async with AsyncSessionFactory() as session:
        kiddo = select(Kiddo).where(Kiddo.id == kiddo_id)
        topics = kiddo.get_topics()
        related_concepts = topics[topic]["concepts"]
    
    return related_concepts

async def get_pdf_concepts(cxt: ToolContext, concepts_context: str) -> list:
    """
    This function retrieves from the vectorial database the chunks of notes related to the pdf
    """
    return query_notes(concepts_context)

concept_choser_agent = LlmAgent(
    name='concept_choser',
    model='gemini-2.0-flash-001',
    description='The agent that chooses a related concept to attach the new node to',
    instruction=CONCEPT_CHOSER_AGENT_INSTRUCTION,
    tools=[get_known_concepts]
)

async def retieve_related_concepts(cxt: ToolContext, concept: str):
    """
    This function retrieves from the database the list of concepts related to the topic
    """
    cxt.state["concept_to_link"] = concept
    agent_tool = AgentTool(agent=concept_choser_agent)
    concepts = await agent_tool.run_async()
    return concepts


async def insert_concept(concept_keyword, cxt: ToolContext) -> Concept:
    """
    This function inserts a new concept into the database.
    """
    if cxt.state["concept_color"] == "1":
        status = LEARNED
    else:
        status = WRONG
    async with AsyncSessionFactory() as session:
        concept = Concept(keyword=concept_keyword, text=concept_keyword, topic=concept_keyword, status=status)
        session.add(concept)
        await session.commit()
        await session.refresh(concept)
    return concept