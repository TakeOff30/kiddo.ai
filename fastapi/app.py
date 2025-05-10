import streamlit as st
import requests

st.title("📄 Caricamento PDF e Invio a API")

# 1. Upload del file PDF
uploaded_file = st.file_uploader("Carica un file PDF", type=["pdf"])

# 2. ID opzionale (es: per associare il file a un oggetto)
kiddo_id = st.text_input("ID oggetto (opzionale)")

# 3. Invia file via HTTP POST
if uploaded_file is not None:
    st.write("Hai caricato:", uploaded_file.name)

    if st.button("📤 Invia a API"):
        # Endpoint dell'API
        endpoint_url = "http://localhost:8000/api/upload-pdf"

        # Costruisci form-data
        files = {
            "file": (uploaded_file.name, uploaded_file, "application/pdf")
        }
        params = {"kiddo_id": kiddo_id}

        try:
            response = requests.post(endpoint_url, files=files, params=params)
            if response.status_code == 200:
                st.success("✅ File inviato con successo!")
                st.json(response.json())
            else:
                st.error(f"❌ Errore {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Errore di rete: {str(e)}")
