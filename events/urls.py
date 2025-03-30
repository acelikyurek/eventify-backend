from django.urls import path
from .views import (
    EventGetAllCreate, EventGetUpdateDelete,
    RegistrationCreateDelete, RegistrationGetAll
)

app_name = "events"

urlpatterns = [
    path("events", EventGetAllCreate.as_view(), name="event-getall-create"),
    path("events/<int:id>", EventGetUpdateDelete.as_view(), name="event-get-update-delete"),
    path("events/<int:event_id>/registrations", RegistrationCreateDelete.as_view(), name="registration-create-delete"),
    path("registrations", RegistrationGetAll.as_view(), name="registration-getall"),
]
