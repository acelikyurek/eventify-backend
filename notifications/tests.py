import pytest
from notifications.tasks import send_email

@pytest.mark.django_db
def test_send_email_task(settings, mailoutbox):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    send_email.apply(args=("Subject", "Body", ["test@example.com"]))

    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.subject == "Subject"
    assert message.body == "Body"
    assert message.to == ["test@example.com"]
