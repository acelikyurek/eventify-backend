import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphene_django.utils.testing import GraphQLTestCase
from events.models import Event
from analytics.schema import schema

User = get_user_model()

@pytest.mark.django_db
class TestEventQueries(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql"

    def setUp(self):
        self.organizer1 = User.objects.create_user(username="org1", password="pass1234")
        self.organizer2 = User.objects.create_user(username="org2", password="pass1234")

        now = timezone.now()
        # Past event
        Event.objects.create(
            title="Past Event",
            description="Already happened",
            date=now - timedelta(days=1),
            location="Offline",
            organizer=self.organizer1,
        )
        # Upcoming events
        Event.objects.create(
            title="Future Event 1",
            description="Coming soon",
            date=now + timedelta(days=1),
            location="Virtual",
            organizer=self.organizer1,
        )
        Event.objects.create(
            title="Future Event 2",
            description="Coming soon too",
            date=now + timedelta(days=2),
            location="Virtual",
            organizer=self.organizer2,
        )

    def test_all_events_query(self):
        response = self.query(
            """
            query {
                allEvents {
                    title
                }
            }
            """
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        assert len(content["data"]["allEvents"]) == Event.objects.count()

    def test_upcoming_events_query(self):
        response = self.query(
            """
            query {
                upcomingEvents {
                    title
                    date
                }
            }
            """
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        upcoming = Event.objects.filter(date__gte=timezone.now()).count()
        assert len(content["data"]["upcomingEvents"]) == upcoming

    def test_event_by_id_query(self):
        event = Event.objects.first()
        response = self.query(
            f"""
            query {{
                event(id: {event.id}) {{
                    title
                    location
                }}
            }}
            """
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        assert content["data"]["event"]["title"] == event.title

        # Nonexistent ID returns null
        response = self.query('query { event(id: 9999) { title } }')
        content = response.json()
        assert content["data"]["event"] is None

    def test_events_by_organizer_query(self):
        response = self.query(
            f"""
            query {{
                eventsByOrganizer(organizerId: {self.organizer1.id}) {{
                    title
                }}
            }}
            """
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        expected = Event.objects.filter(organizer=self.organizer1).count()
        assert len(content["data"]["eventsByOrganizer"]) == expected
