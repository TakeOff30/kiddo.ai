import streamlit as st
import requests

st.title("Invio PDF al server con Kiddo ID in query string")

# Inserisci Kiddo ID
kiddo_id = st.number_input("Inserisci il Kiddo ID", min_value=0, step=1)

# Upload PDF
uploaded_file = st.file_uploader("Carica il PDF", type=["pdf"])

# Invio al server
if uploaded_file is not None and kiddo_id is not None:
    if st.button("Invia al server"):
        try:
            # Costruzione URL con parametro in query string
            url = f"http://localhost:8000/api/upload-pdf?kiddo_id={kiddo_id}"

            # Prepara file da inviare come multipart/form-data
            files = {
                "file": (uploaded_file.name, uploaded_file, "application/pdf")
            }

            response = requests.post(url, files=files)

            if response.status_code == 200:
                st.success("PDF caricato correttamente!")
                st.text(response.text)
            else:
                st.error(f"Errore dal server: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Errore nella richiesta: {e}")
