from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from myproject.lms.models import Lesson, CourseSubscription


class BaseTestSetup(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.regular_user = User.objects.create_user(username='user', password='userpass')
        self.client = APIClient()

class LessonCRUDTests(BaseTestSetup):
    def test_create_lesson_admin(self):
        self.client.login(username='admin', password='adminpass')
        data = {"title": "Урок 1", "content": "Содержимое урока"}
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], data['title'])

    def test_create_lesson_regular_user_forbidden(self):
        self.client.login(username='user', password='userpass')
        data = {"title": "Урок 2", "content": "Содержимое урока"}
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_read_lesson(self):
        # Создаем урок напрямую
        lesson = Lesson.objects.create(title='Тестовый урок', content='Тест')
        response = self.client.get(f'/api/lessons/{lesson.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Тестовый урок')

    def test_update_lesson_admin(self):
        self.client.login(username='admin', password='adminpass')
        lesson = Lesson.objects.create(title='Урок до', content='До обновления')
        data = {"title": "Урок после", "content": "После обновления"}
        response = self.client.put(f'/api/lessons/{lesson.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], data['title'])

    def test_delete_lesson_admin(self):
        self.client.login(username='admin', password='adminpass')
        lesson = Lesson.objects.create(title='Удаляемый урок', content='Контент')
        response = self.client.delete(f'/api/lessons/{lesson.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())

class SubscriptionCRUDTests(BaseTestSetup):
    def test_create_subscription_user(self):
        self.client.login(username='user', password='userpass')
        data = {"user": self.regular_user.id, "plan": "basic", "status": "active"}
        response = self.client.post('/api/subscriptions/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['plan'], 'basic')

    def test_read_subscriptions_admin(self):
        CourseSubscription.objects.create(user=self.regular_user, plan='basic', status='active')
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/api/subscriptions/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

    def test_update_subscription_forbidden(self):
        sub = CourseSubscription.objects.create(user=self.regular_user, plan='basic', status='active')
        self.client.login(username='user', password='userpass')
        data = {"plan": "premium", "status": "active"}
        response = self.client.put(f'/api/subscriptions/{sub.id}/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_subscription_admin(self):
        sub = CourseSubscription.objects.create(user=self.regular_user, plan='basic', status='active')
        self.client.login(username='admin', password='adminpass')
        response = self.client.delete(f'/api/subscriptions/{sub.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CourseSubscription.objects.filter(id=sub.id).exists())
