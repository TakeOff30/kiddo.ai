from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Response
from sqlmodel import SQLModel, Field, select # O from sqlalchemy.future import select ecc.
from typing import List, Optional
from rag import load_pdf_on_vector_db
from item import Item
import tempfile
import os

# Importa la dipendenza e (se usi SQLModel) la funzione di inizializzazione
from db import create_tables, get_session
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Avvio dell'applicazione in corso...")
    await create_tables()
    print("Setup del database completato.")

    yield

    print("Spegnimento dell'applicazione...")



app = FastAPI(lifespan=lifespan)

# ENDPOINTS

@app.post("/upload-pdf")
def upload_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
        
    try:
        load_pdf_on_vector_db(tmp_path)
        return Response(content="PDF loaded", media_type="text/plain")
    finally:
        os.remove(tmp_path)