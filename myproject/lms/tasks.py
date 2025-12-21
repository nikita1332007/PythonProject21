from datetime import timezone, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


@shared_task
def send_course_update_email(user_email, course_title):
    send_mail(
        subject=f'Обновление курса: {course_title}',
        message=f'Здравствуйте! В курсе "{course_title}" появились новые материалы.',
        from_email='no-reply@yourdomain.com',
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def block_inactive_users():
    User = get_user_model()
    one_month_ago = timezone.now() - timedelta(days=30)
    users_to_block = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    for user in users_to_block:
        user.is_active = False
        user.save()