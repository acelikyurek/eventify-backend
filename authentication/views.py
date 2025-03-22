from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.serializers import RegisterSerializer

class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
