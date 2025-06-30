from api.adk.models.pdf_extraction_output import PdfExtractionOutput
from api.adk.tools.kiddo_tools import get_known_concepts, retrieve_topic, get_unknown_concepts, retrieve_related_concepts, study_type_setter, topic_setter
from api.adk.tools.pdf_tools import save_topic_on_db
from google.adk.agents import Agent, SequentialAgent
from .prompts import KIDDO_AGENT_INSTRUCTION, QUESTIONER_AGENT_INSTRUCTION, PDF_EXTRACTOR_AGENT_INSTRUCTION, CONCEPT_CLASSIFIER_AGENT_INSTRUCTION, RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION

# PDF ingestion's agent
pdf_extractor_agent = Agent(
    name='pdf_extractor_agent',
    model='gemini-2.0-flash-001',
    description='The agent that extracts the text from the PDF and saves it on the database',
    output_schema=PdfExtractionOutput,
    # output_key='topics', # Salva il risultato in state['topics']
    instruction=PDF_EXTRACTOR_AGENT_INSTRUCTION,
)

# Kiddo's agents
concept_classifier_agent = Agent(
    name='concept_classifier_agent',
    model='gemini-2.0-flash-001',
    description='The agent that establishes the correctness of user\'s answare to Kiddo\'s question',
    instruction=CONCEPT_CLASSIFIER_AGENT_INSTRUCTION,
    tools=[],
    output_key='concept_color'
)

related_concept_choser_agent = Agent(
    name='related_concept_choser_agent',
    model='gemini-2.0-flash-001',
    description='The agent that chooses a related concept to attach the new node to',
    instruction= RELATED_CONCEPT_CHOOSER_AGENT_INSTRUCTION,
    tools=[retrieve_related_concepts]
)

node_addition_agent = SequentialAgent(
    name='node_addition_agent',
    description='The agent that classifies user\'s answare and adds nodes to the graph',
    sub_agents=[related_concept_choser_agent, concept_classifier_agent],
)

questioner_agent = Agent(
    model='gemini-2.0-flash-001',
    name='questioner_agent',
    description='The agent that generates questions based on what the Kiddo knows and what it does not know',
    instruction=QUESTIONER_AGENT_INSTRUCTION,
    output_key='last_question',
    tools=[get_unknown_concepts, get_known_concepts]
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='The main agent simulating the Kiddo',
    instruction=KIDDO_AGENT_INSTRUCTION,
    tools=[topic_setter, study_type_setter],
    sub_agents=[questioner_agent, node_addition_agent],
)

