from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserProfileSerializer, UserDetailSerializer
from ..lms.serializers import UserCreateSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = []

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return UserDetailSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            if self.request.user != self.get_object():
                self.permission_denied(self.request, message="Cannot edit others' profiles")
        return super().get_permissions()
