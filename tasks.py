from app import celery

@celery.task
def sample_task():
    return "Hello from Celery!"
