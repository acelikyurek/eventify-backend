import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from django.contrib.auth.models import User
from events.models import Event

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = ("id", "title", "description", "date", "location", "organizer", "created_at")

class Query(graphene.ObjectType):
    all_events = graphene.List(EventType)
    upcoming_events = graphene.List(EventType)
    event = graphene.Field(EventType, id=graphene.ID(required=True))
    events_by_organizer = graphene.List(EventType, organizer_id=graphene.ID(required=True))

    def resolve_all_events(self, info):
        return Event.objects.order_by("-date").all()

    def resolve_upcoming_events(self, info):
        return Event.objects.filter(date__gte=timezone.now()).order_by("date")

    def resolve_event(self, info, id):
        try:
            return Event.objects.get(pk=id)
        except Event.DoesNotExist:
            return None

    def resolve_events_by_organizer(self, info, organizer_id):
        return Event.objects.filter(organizer__id=organizer_id).order_by("-date")

schema = graphene.Schema(query=Query)
