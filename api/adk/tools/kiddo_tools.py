import json
from api.adk.prompts import CONCEPT_CHOOSER_AGENT_INSTRUCTION
from api.constants.concept_status import LEARNED, CREATED, WRONG, TO_BE_REPEATED
from api.models.kiddo import Kiddo
from sqlmodel import select
from api.db import AsyncSessionFactory
from sqlmodel import select
from api.models.concept import Concept
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import LlmAgent
import datetime


def topic_setter(topic: str, tool_context: ToolContext):
    """
    This function sets the topic for the Kiddo. It is used to set the topic for the Kiddo.
    Args:
        topic (str): The topic to set for the Kiddo.
        tool_context (ToolContext): Automatically provided by ADK, do not specify when calling.
    """

    print("XXXXXXX")
    print("topic_setter INVOKED")
    print(f"topic: {topic}")
    print("YYYYYY")
    print()

    tool_context.state["topic"] = topic
    return {
        "status": "success",
        "message": f"Topic set to {topic}",
    }

def study_type_setter(study_type: str, tool_context: ToolContext):
    """
    This function sets the study type for the Kiddo. It is used to set the study type for the Kiddo.

    Args:
        study_type (str): The type of study, either "new_concept" or "review".
        tool_context (ToolContext): Automatically provided by ADK, do not specify when calling.
    """

    print("XXXXXXX")
    print("study_type_setter INVOKED")
    print(f"study_type: {study_type}")
    print("YYYYYY")
    print()

    tool_context.state["study_type"] = study_type
    return {
        "status": "success",
        "message": f"Study type set to {study_type}",
    }

async def get_concepts(topic: str, ctx: ToolContext, status: list[str]) -> dict:
    topics_key = "user:topics"  # Persistent state key
    topics = ctx.state.get(topics_key, {})  # Recupera dizionario esistente o uno nuovo

    # TODO: Filter by Kiddo Id
    async with AsyncSessionFactory() as session:
        query = select(Concept).where(Concept.topic == topic, Concept.status.in_(status))
        result = await session.execute(query)
        concepts_list = result.scalars().all()

    texts = [c.text for c in concepts_list]

    # ✅ Aggiorna il dizionario con il topic corrente
    topics[topic] = texts

    # ✅ Salva nel context state
    ctx.state[topics_key] = topics

    print("VVVVVVV")
    print(ctx.state[topics_key][topic])

    return {
        "status": "success",
        "message": "Topic's known concepts loaded into state in {user:topics} in topic's key",
    }



async def get_known_concepts(topic: str, tool_context: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has learned so far.

    Args:
        topic: The topic for which to retrieve known concepts.
        tool_context: Automatically provided by ADK, do not specify when calling.
        
    Returns:
        dict: Status of the get concepts operation.
    """
    print("XXXXXXX")
    print("get_known_concepts INVOKED")
    print(f"topic: {topic}")
    print("YYYYYY")
    print()

    await get_concepts(topic, tool_context, status=[ LEARNED ])

    return {
        "status": "success",
        "message": "Topic's known concepts loaded into state in {user:topics} in topic's key",
    }


async def get_unknown_concepts(topic: str, tool_context: ToolContext) -> list:
    """
    This function retrieves from the database the list of concepts that the Kiddo 
    has not learned yet.

    Args:
        topic: The topic for which to retrieve unknown concepts.
        ctx: Automatically provided by ADK, do not specify when calling.
        
    Returns:
        dict: Status of the get concepts operation.
    """
    print("XXXXXXX")
    print("get_unknown_concepts INVOKED")
    print(f"topic: {topic}")
    print("YYYYYY")
    print()

    await get_concepts(topic, tool_context, status=[ CREATED ])

    return {
        "status": "success",
        "message": "Topic's unknown concepts loaded into state in {user:topics} in topic's key",
    }



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