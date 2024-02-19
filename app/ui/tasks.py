from celery import shared_task


@shared_task
def start_etl_process():
    return 5 * 8
