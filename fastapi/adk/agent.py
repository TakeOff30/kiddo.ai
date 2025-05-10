from fastapi.adk.tools.kiddo_tools import get_known_concepts, retrieve_topic
from fastapi.adk.tools.pdf_tools import save_topic_on_db
from fastapi.services.vector_db_service import query_notes
from google.adk.agents import Agent, LlmAgent, SequentialAgent
from .prompts import KIDDO_AGENT, QUESTIONER_AGENT, PDF_EXTRACTOR_AGENT

# PDF ingestion's angents
pdf_extractor_agent = LlmAgent(
    name='pdf_extractor_agent',
    model='gemini-2.0-flash-001',
    description='The agent that extracts the text from the PDF and saves it on the database',
    instruction=PDF_EXTRACTOR_AGENT,
    tools=[save_topic_on_db]
)


# Kiddo's agents
concept_classifier_agent = LlmAgent(
    name='concept_classifier_agent',
    model='gemini-2.0-flash-001',
    description='The agent that establishes the correctness of the Kiddo\'s understanding of a concept',
    #instruction=
    tools=[query_notes]
)

related_concept_choser_agent = LlmAgent(
    name='related_concept_choser_agent',
    model='gemini-2.0-flash-001',
    description='The agent that chooses a related concept to attach the new node to',
    #instruction=
    tools=[get_known_concepts]
)

node_addition_agent = SequentialAgent(
    name='node_addition_agent',
    description='The agent that adds nodes to the graph',
    sub_agents=[related_concept_choser_agent, concept_classifier_agent],
)

questioner_agent = LlmAgent(
    model='gemini-2.0-flash-001',
    name='questioner_agent',
    description='The agent that generates questions curious questions a kid would do',
    instruction=QUESTIONER_AGENT,
    tools=[retrieve_topic]
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='The main agent simulating the Kiddo',
    instruction=KIDDO_AGENT,
)

