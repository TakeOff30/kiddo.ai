# import streamlit as st
# import requests

# st.title("📄 Caricamento PDF e Invio a API")

# # 1. Upload del file PDF
# uploaded_file = st.file_uploader("Carica un file PDF", type=["pdf"])

# # 2. ID opzionale (es: per associare il file a un oggetto)
# kiddo_id = st.text_input("ID oggetto (opzionale)")

# # 3. Invia file via HTTP POST
# if uploaded_file is not None:
#     st.write("Hai caricato:", uploaded_file.name)

#     if st.button("📤 Invia a API"):
#         # Endpoint dell'API
#         endpoint_url = "http://localhost:8000/api/upload-pdf"

#         # Costruisci form-data
#         files = {
#             "file": (uploaded_file.name, uploaded_file, "application/pdf")
#         }
#         params = {"kiddo_id": kiddo_id}

#         try:
#             response = requests.post(endpoint_url, files=files, params=params)
#             if response.status_code == 200:
#                 st.success("✅ File inviato con successo!")
#                 st.json(response.json())
#             else:
#                 st.error(f"❌ Errore {response.status_code}: {response.text}")
#         except Exception as e:
#             st.error(f"⚠️ Errore di rete: {str(e)}")

import streamlit as st
import graphviz # Per la visualizzazione del grafo

# --- Configurazione della Pagina ---
st.set_page_config(layout="wide", page_title="Grafo & Chatbot")

st.title("Applicazione Interattiva: Creazione Grafo e Chatbot")
st.markdown("---")

# --- Sezione Creazione Grafo ---

st.markdown("---")

# --- Sezione Chatbot ---
st.header("Card Chatbot")

# Inizializzazione dello stato della sessione per la chat (se non esiste già)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Come posso aiutarti oggi?"}]

# Visualizzazione dei messaggi della chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input dell'utente
if prompt := st.chat_input("Scrivi il tuo messaggio..."):
    # Aggiungi il messaggio dell'utente alla history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Risposta del Chatbot (semplice eco o logica più complessa)
    # Qui puoi integrare la logica del tuo chatbot (es. chiamate a API LLM, ecc.)
    response_text = f"Hai detto: \"{prompt}\". Sto ancora imparando!" # Esempio di risposta

    # Aggiungi la risposta del bot alla history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

st.markdown("---")
st.caption("Pagina creata con Streamlit.")