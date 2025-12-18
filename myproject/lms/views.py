from django.contrib.auth.models import User
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .permissions import IsModeratorOrReadOnly, IsOwnerOrModerator
from .serializers import CourseSerializer, LessonSerializer, UserCreateSerializer, UserSerializer
from ..users.models import Payment
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PaymentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, IsModeratorOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        return [permission() for permission in permission_classes]


class LessonListCreate(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'amount', 'date']
    ordering_fields = ['date', 'amount']


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
