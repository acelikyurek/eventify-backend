from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from events.models import Event, Registration

User = get_user_model()

class EventTests(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create_user("org", "org@example.com", "pass1234")
        self.attendee = User.objects.create_user("att", "att@example.com", "pass1234")
        self.client = APIClient()

    def test_list_events(self):
        url = reverse("events:event-getall-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event_auth_required(self):
        url = reverse("events:event-getall-create")
        data = {"title":"Test","date":"2025-04-01T10:00:00Z","location":"Online"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.organizer)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_delete_permissions(self):
        event = Event.objects.create(title="E", date="2025-05-01T10:00:00Z", location="X", organizer=self.organizer)
        url = reverse("events:event-get-update-delete", args=[event.id])

        self.client.force_authenticate(user=self.attendee)
        resp = self.client.put(url, {"title":"New"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.organizer)
        resp = self.client.put(url, {"title":"New","date":"2025-05-01T10:00:00Z","location":"X"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_registration_flow(self):
        event = Event.objects.create(title="E", date="2025-06-01T10:00:00Z", location="Y", organizer=self.organizer)
        register_url = reverse("events:registration-create", args=[event.id])

        self.client.force_authenticate(user=self.attendee)

        resp1 = self.client.post(register_url)
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        reg_id = resp1.data["id"]

        resp2 = self.client.post(register_url)
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

        delete_url = reverse("events:registration-delete", args=[event.id, reg_id])
        resp3 = self.client.delete(delete_url)
        self.assertEqual(resp3.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_registrations_list(self):
        event = Event.objects.create(title="E", date="2025-06-01T10:00:00Z", location="Z", organizer=self.organizer)
        Registration.objects.create(user=self.attendee, event=event)

        url = reverse("events:registration-getall")
        self.client.force_authenticate(user=self.attendee)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
