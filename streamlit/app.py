import requests
import streamlit as st


API_BASE_URL = "http://fastapi:8000"


def fetch_root_api():
        response = requests.post(f"{API_BASE_URL}/palaces")
        return response.json()

palaces_list = fetch_root_api()
st.header(f"🏛️ Palazzo: {palaces_list}")