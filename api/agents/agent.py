from agents import Agent
from api.agents.models.pdf_extraction_output import PdfExtractionOutput
from api.agents.tools.kiddo_tools import get_known_concepts, retrieve_topic, get_unknown_concepts, retrieve_related_concepts
from api.agents.tools.pdf_tools import save_topic_on_db
from .prompts import KIDDO_AGENT_INSTRUCTION, QUESTIONER_AGENT_INSTRUCTION, PDF_EXTRACTOR_AGENT_INSTRUCTION, CONCEPT_CLASSIFIER_AGENT_INSTRUCTION, RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION

# PDF ingestion's agent
pdf_extractor_agent = Agent(
    name='pdf_extractor_agent',
    instructions=PDF_EXTRACTOR_AGENT_INSTRUCTION,
    output_type=PdfExtractionOutput,
)

# Kiddo's agents
concept_classifier_agent = Agent(
    name='concept_classifier_agent',
    handoff_description='The agent that establishes the correctness of the Kiddo\'s understanding of a concept',
    instructions=CONCEPT_CLASSIFIER_AGENT_INSTRUCTION,
    tools=[],
)

related_concept_choser_agent = Agent(
    name='related_concept_choser_agent',
    handoff_description='The agent that chooses a related concept to attach the new node to',
    instructions= RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION,
    tools=[retrieve_related_concepts]
)

node_addition_agent = Agent(
    name='node_addition_agent',
    handoff_description='The agent that adds nodes to the graph',
    handoffs=[related_concept_choser_agent, concept_classifier_agent],
)

questioner_agent = Agent(
    name='questioner_agent',
    handoff_description='The agent that generates questions curious questions a kid would do',
    instructions=QUESTIONER_AGENT_INSTRUCTION,
    tools=[get_known_concepts, get_unknown_concepts]
)

root_agent = Agent(
    name='root_agent',
    instructions=KIDDO_AGENT_INSTRUCTION,
    handoffs=[questioner_agent, node_addition_agent],
)

