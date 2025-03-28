from rest_framework import serializers
from .models import Event, Registration

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source="organizer.id")

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("organizer", "created_at", "updated_at")

class RegistrationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    event = serializers.ReadOnlyField(source="event.id")

    class Meta:
        model = Registration
        fields = ("id", "user", "event", "created_at")
