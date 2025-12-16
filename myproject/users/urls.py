from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserProfileViewSet

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
