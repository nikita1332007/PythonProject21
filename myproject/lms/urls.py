from django.urls import path
from .views import CourseSubscriptionAPIView

urlpatterns = [
    path('course-subscription/', CourseSubscriptionAPIView.as_view(), name='course-subscription'),
]