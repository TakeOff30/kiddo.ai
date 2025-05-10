from fastapi.adk.tools.pdf_tools import save_topic_on_db
from fastapi.adk.utils import load_instruction_from_file
from google.adk.agents import Agent

pdf_extractor_agent = Agent(
    model='gemini-2.5-pro',
    name='pdf_extractor_agent',
    description='Extracts macro area and concepts from PDF file and stores them in the vec_db and SQL DB',
    instruction=load_instruction_from_file("pdf_extractor_agent_instructions.txt"),
    tools=[save_topic_on_db],
)
