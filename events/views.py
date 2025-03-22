from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer
from notifications.tasks import send_email

class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.organizer == request.user

@method_decorator(cache_page(60*5), name="get")
class EventListCreate(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)

        send_email.delay(
            subject="Event Published",
            message=f"Your event '{event.title}' is now live.",
            recipient_list=[self.request.user.email],
        )

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizer)

class RegistrationCreate(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs["event_id"])
        if Registration.objects.filter(user=self.request.user, event=event).exists():
            raise ValidationError("Already registered!")
        serializer.save(user=self.request.user, event=event)

        send_email.delay(
            subject=f"Registered for {event.title}",
            message=f"You are confirmed for {event.title} on {event.date}.",
            recipient_list=[self.request.user.email],
        )

class RegistrationDelete(generics.DestroyAPIView):
    queryset = Registration.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("Cannot delete others' registrations!")
        return obj

    def perform_destroy(self, instance):
        event = instance.event
        user_email = instance.user.email
        super().perform_destroy(instance)

        send_email.delay(
            subject=f"Cancelled: {event.title}",
            message=f"Your registration for {event.title} has been cancelled.",
            recipient_list=[user_email],
        )

class UserRegistrationsList(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user_id = int(self.kwargs["user_id"])
        if self.request.user.id != user_id:
            raise PermissionDenied("Cannot view others' registrations!")
        return Registration.objects.filter(user__id=user_id)
