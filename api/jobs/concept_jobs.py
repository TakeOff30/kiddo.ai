from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlmodel import select
from api.constants.concept_status import FORGOTTEN, TO_BE_REPEATED
from api.db import AsyncSessionFactory
from api.models.concept import Concept
from api.models.kiddo import Kiddo

scheduler = BlockingScheduler()

@scheduler.set_concepts_forgotten('cron', day_of_week='mon-sun', hour=1)
async def set_concepts_forgotten():
    twenty_four_hours_ago = datetime.now(datetime.timezone.utc) - timedelta(hours=24)
    async with AsyncSessionFactory() as session:
        concepts_to_review = await session.execute(
            select(Concept).where(
                Concept.status == TO_BE_REPEATED, 
                Concept.created_at < twenty_four_hours_ago
            )
        )
    
    concepts = concepts_to_review.scalars().all()

    for concept in concepts:
        concept.status = FORGOTTEN

    await session.commit()

scheduler.start()
