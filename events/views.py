from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer
from notifications.tasks import send_email
from rest_framework import mixins
from django.http import Http404

class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.organizer == request.user

@method_decorator(cache_page(60*5), name="get")
class EventGetAllCreate(generics.ListCreateAPIView):
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

class EventGetUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizer)
    lookup_field = "id"

class RegistrationCreateDelete(generics.GenericAPIView, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return Registration.objects.filter(user=self.request.user, event__id=event_id)

    def get_object(self):
        try:
            return self.get_queryset().get()
        except Registration.DoesNotExist:
            raise Http404

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

    def perform_destroy(self, instance):
        event = instance.event
        user_email = instance.user.email
        super().perform_destroy(instance)

        send_email.delay(
            subject=f"Cancelled: {event.title}",
            message=f"Your registration for {event.title} has been cancelled.",
            recipient_list=[user_email],
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class RegistrationGetAll(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)
