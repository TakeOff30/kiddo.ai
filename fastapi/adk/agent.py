from google.adk.agents import Agent, LlmAgent, SequentialAgent
from .prompts import KIDDO_AGENT, QUESTIONER_AGENT
from ..rag import query_notes

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
    tools=[retieve_topic]
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='The main agent simulating the Kiddo',
    instruction=KIDDO_AGENT,
)

