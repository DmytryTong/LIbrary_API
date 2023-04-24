from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer

from django.shortcuts import redirect
from allauth.account.views import LogoutView


class CustomLogoutView(LogoutView):
    def get_next_url(self):
        return "/my-redirect-url/"

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        response = redirect(self.get_next_url())
        return response


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
