from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from . import permissions
from .models import Course, Lesson, CourseSubscription
from .paginators import StandardResultsSetPagination
from .permissions import IsModeratorOrReadOnly, IsOwnerOrModerator
from .serializers import CourseSerializer, LessonSerializer
from .services import stripe_service
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

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'amount', 'date']
    ordering_fields = ['date', 'amount']

class CourseSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({'error': 'Поле course_id обязательно'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        subscription = CourseSubscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
        else:
            CourseSubscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({'message': message})


class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


        product_resp = stripe_service.create_stripe_product(name=course.title, description=course.description or "")
        if "error" in product_resp:
            return Response({"error": product_resp["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        price_cents = int(course.price * 100)
        price_resp = stripe_service.create_stripe_price(product_id=product_resp.id, unit_amount=price_cents)
        if "error" in price_resp:
            return Response({"error": price_resp["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        success_url = request.build_absolute_uri('/payments/success/')
        cancel_url = request.build_absolute_uri('/payments/cancel/')

        session_resp = stripe_service.create_checkout_session(price_id=price_resp.id,
                                                              success_url=success_url,
                                                              cancel_url=cancel_url)
        if "error" in session_resp:
            return Response({"error": session_resp["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        payment = Payment.objects.create(
            user=request.user,
            course=course,
            stripe_product_id=product_resp.id,
            stripe_price_id=price_resp.id,
            stripe_session_id=session_resp.id,
            amount=course.price,
            status='pending',
            payment_url=session_resp.url,
        )

        return Response({
            "payment_id": payment.id,
            "payment_url": session_resp.url,
            "stripe_session_id": session_resp.id,
        }, status=status.HTTP_201_CREATED)

class PaymentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        session_resp = stripe_service.retrieve_checkout_session(payment.stripe_session_id)
        if "error" in session_resp:
            return Response({"error": session_resp["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({
            "payment_id": payment.id,
            "status": session_resp.payment_status,
            "amount_total": session_resp.amount_total,
            "currency": session_resp.currency,
        })
