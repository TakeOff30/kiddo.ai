from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.set_concepts_forgotten('cron', day_of_week='mon-sun', hour=1)
def set_concepts_forgotten():
    return

scheduler.start()
