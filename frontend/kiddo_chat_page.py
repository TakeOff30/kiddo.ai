import streamlit as st
import requests
from typing import List, Dict

# Configurazione della pagina
st.set_page_config(
    page_title="Chat con Kiddo",
    page_icon="🤖",
    layout="wide"
)


def start_new_session():
    try:
        headers = { "Content-Type": "application/json" }
        response = requests.post(
            "http://localhost:8000/api/new_chat",
            headers=headers,
            timeout=30  # timeout di 30 secondi
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            return response_data
        else:
            return f"Errore nell'API locale: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Errore di connessione: Assicurati che il server sia in esecuzione su http://localhost:8000"
    except requests.exceptions.Timeout:
        return "⏱️ Timeout: Il server ha impiegato troppo tempo a rispondere"
    except Exception as e:
        return f"Errore nell'API locale: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    response = start_new_session()
    st.session_state.session_id = response["session_id"]
    st.session_state.messages.append({"role": "assistant", "content": response["first_message"]})

def get_kiddo_response(message: str) -> str:
    """Chiama l'API locale del LLM su localhost:8000"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            return response_data["message"]
        else:
            return f"Errore nell'API locale: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Errore di connessione: Assicurati che il server sia in esecuzione su http://localhost:8000"
    except requests.exceptions.Timeout:
        return "⏱️ Timeout: Il server ha impiegato troppo tempo a rispondere"
    except Exception as e:
        return f"Errore nell'API locale: {str(e)}"

with st.sidebar:
    st.title("⚙️ Configurazioni")
    
    if st.button("Nuova chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Chat con Kiddo")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Scrivi il tuo messaggio..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = get_kiddo_response(prompt)
                
                st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Errore: {str(e)}")
