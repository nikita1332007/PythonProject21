from django.urls import path
from .views import CourseSubscriptionAPIView, CreatePaymentView, PaymentStatusView

urlpatterns = [
    path('course-subscription/', CourseSubscriptionAPIView.as_view(), name='course-subscription'),
    path('payments/create/', CreatePaymentView.as_view(), name='create-payment'),
    path('payments/status/<int:payment_id>/', PaymentStatusView.as_view(), name='payment-status'),
]