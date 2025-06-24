from agents import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "my_app"
USER_ID = "my_user"
SESSION_ID = "session_id"

async def run_agent(agent, content):
    result = await Runner.run(agent, content)

    return result.final_output
    

def build_string_content(prompt):
    return types.Content(role="user", parts=[types.Part(text=prompt)])

def build_pdf_content(file_id: str):
    return {
                "role": "user",
                "content": [{"type": "input_file", "file_id": file_id}],
            }

def get_session_events(session_service, session_id):
    return session_service.get_session(app_name="my_app", user_id="my_user", session_id=session_id).events