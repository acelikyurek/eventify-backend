from django.urls import path
from .views import (
    EventListCreate, EventDetail,
    RegistrationCreate, RegistrationDelete, UserRegistrationsList
)

app_name = "events"

urlpatterns = [
    path("events", EventListCreate.as_view(), name="event-list"),
    path("events/<int:pk>", EventDetail.as_view(), name="event-detail"),
    path("events/<int:event_id>/register", RegistrationCreate.as_view(), name="event-register"),
    path("registrations/<int:pk>", RegistrationDelete.as_view(), name="registration-delete"),
    path("users/<int:user_id>/registrations", UserRegistrationsList.as_view(), name="user-registrations"),
]
