import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

metadata = SQLModel.metadata

DATABASE_URL = os.getenv("DATABASE_URL")

engine_async = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionFactory = sessionmaker(
    bind=engine_async,        # Collega la fabbrica all'engine
    class_=AsyncSession,      # Specifica che deve creare sessioni asincrone
    expire_on_commit=False    # è utile per non dover ricaricare gli oggetti dopo un commit
)

async def get_session() -> AsyncSession:
    """Dependency function that yields an async session."""
    async with AsyncSessionFactory() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise

async def create_tables():
    async with engine_async.begin() as conn:
        await conn.run_sync(metadata.create_all)
