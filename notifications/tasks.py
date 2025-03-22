from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True)
def send_email(self, subject, message, recipient_list):
    send_mail(subject, message, "no-reply@eventify.com", recipient_list)
