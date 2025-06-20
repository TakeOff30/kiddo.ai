from api.adk.tools.kiddo_tools import get_known_concepts, retrieve_topic, get_unknown_concepts, retrieve_related_concepts
from api.adk.tools.pdf_tools import save_topic_on_db
from google.adk.agents import Agent, LlmAgent, SequentialAgent
from .prompts import KIDDO_AGENT_INSTRUCTION, QUESTIONER_AGENT_INSTRUCTION, PDF_EXTRACTOR_AGENT_INSTRUCTION, CONCEPT_CLASSIFIER_AGENT_INSTRUCTION, RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION

# PDF ingestion's agent
pdf_extractor_agent = LlmAgent(
    name='pdf_extractor_agent',
    model='gemini-2.0-flash-001',
    description='The agent that extracts the text from the PDF and saves it on the database',
    instruction=PDF_EXTRACTOR_AGENT_INSTRUCTION,
)

# Kiddo's agents
concept_classifier_agent = LlmAgent(
    name='concept_classifier_agent',
    model='gemini-2.0-flash-001',
    description='The agent that establishes the correctness of the Kiddo\'s understanding of a concept',
    instruction=CONCEPT_CLASSIFIER_AGENT_INSTRUCTION,
    tools=[],
    output_key='concept_color'
)

related_concept_choser_agent = LlmAgent(
    name='related_concept_choser_agent',
    model='gemini-2.0-flash-001',
    description='The agent that chooses a related concept to attach the new node to',
    instruction= RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION,
    tools=[retrieve_related_concepts]
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
    instruction=QUESTIONER_AGENT_INSTRUCTION,
    tools=[get_known_concepts, get_unknown_concepts]
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='The main agent simulating the Kiddo',
    instruction=KIDDO_AGENT_INSTRUCTION,
    sub_agents=[questioner_agent, node_addition_agent],
)

