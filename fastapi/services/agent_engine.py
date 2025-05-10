from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "appname"
USER_ID = "user"

def run_agent(agent, content, session_id, session_obj = None):
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    if session_obj:
        set_state(session.state, session_obj)

    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print(f"Final response: {final_response}")
    

def build_string_content(prompt):
    return types.Content(role="user", parts=[types.Part(text=prompt)])

def build_pdf_content(image_bytes):
    return types.Content(role="user", parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="application/pdf"),
            ])

def set_state(state, session_obj):
    for key, value in session_obj.items():
        state[key] = value