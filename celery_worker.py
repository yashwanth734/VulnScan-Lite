from celery import Celery

celery = Celery(
    'myflaskapp',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
