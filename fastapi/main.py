from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, select # O from sqlalchemy.future import select ecc.
from typing import List, Optional

from item import Item

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

@app.post("/palaces/", response_model=Item)
async def create_item(db: AsyncSession = Depends(get_session)):
    item = Item(name="Palazzo Ducale", description="Un palazzo storico a Venezia")
    db.add(item)
    await db.commit()
    await db.refresh(item) # Ricarica l'item per avere l'ID generato
    return item

@app.get("/palaces/", response_model=List[Item])
async def read_items(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items