from http.client import CREATED
from api.adk.prompts import CONCEPT_CHOOSER_AGENT_INSTRUCTION
from api.constants.concept_status import LEARNED, WRONG, TO_BE_REPEATED
from api.models.kiddo import Kiddo
from sqlmodel import select
from api.db import AsyncSessionFactory
from sqlmodel import select
from api.models.concept import Concept
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import LlmAgent
import datetime


async def get_concepts(topic: str, ctx: ToolContext, status: list[str]) -> dict:
    topic_key = f"user:topics"  # Using user: prefix makes this persistent across sessions
    topics = ctx.state.get(topic_key, {})

    # TODO: Filter by Kiddo Id
    concepts_list = []
    async with AsyncSessionFactory() as session:
        query = select(Concept).where(Concept.topic == topic, Concept.status.in_(status))
        result = await session.execute(query)
        concepts_list = result.scalars().all()

    texts = [c.text for c in concepts_list]
    topics[topic] = texts


    return {
        "status": "success",
        "message": "Topic's known concepts loaded into state in {user:topics} in topic's key",
    }


async def get_known_concepts(topic: str, cxt: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has learned so far.

    Args:
        topic: The topic for which to retrieve known concepts.
        ctx: Automatically provided by ADK, do not specify when calling.
        
    Returns:
        dict: Status of the get concepts operation.
    """
    get_concepts(topic, cxt, status=[ LEARNED ])


async def get_known_concepts(topic: str, cxt: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has not learned yet.

    Args:
        topic: The topic for which to retrieve unknown concepts.
        ctx: Automatically provided by ADK, do not specify when calling.
        
    Returns:
        dict: Status of the get concepts operation.
    """
    get_concepts(topic, cxt, status=[ CREATED ])



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
    return ""

concept_choser_agent = LlmAgent(
    name='concept_choser',
    model='gemini-2.0-flash-001',
    description='The agent that chooses a related concept to attach the new node to',
    instruction=CONCEPT_CHOOSER_AGENT_INSTRUCTION,
    tools=[get_known_concepts]
)

async def retrieve_related_concepts(cxt: ToolContext, concept: str):
    """
    This function retrieves from the database the list of concepts related to the topic
    """
    cxt.state["concept_to_link"] = concept
    agent_tool = AgentTool(agent=concept_choser_agent)
    concepts = await agent_tool.run_async()
    return concepts


async def insert_concept(concept_keyword, cxt: ToolContext):
    """
    This function inserts a new concept into the database.
    """
    if cxt.state["concept_color"] == "1":
        status = TO_BE_REPEATED
    else:
        status = WRONG
    async with AsyncSessionFactory() as session:
        concept = Concept(
            keyword=concept_keyword, 
            text=concept_keyword, 
            topic=concept_keyword, 
            status=status, 
            last_repetion=datetime.now(datetime.timezone.utc), 
            kiddo_id=cxt.state["kiddo_id"],
        )
        session.add(concept)
        await session.commit()
        await session.refresh(concept)