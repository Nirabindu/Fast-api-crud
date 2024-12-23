from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import create_message, mail

c_app = Celery()
c_app.config_from_object("src.config")


@c_app.task()
def send_mail(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)
    # celery not support any asyncIo task
    # so if we needs to run asynchronous task/function inside celery needs
    # to convert them into sync first
    async_to_sync(mail.send_message)(message)
    print("Email sent")
