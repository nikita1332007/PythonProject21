from django.contrib.auth.models import User
from django.contrib.postgres import serializers

from .models import Course, Lesson
from ..users.models import Payment


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'lessons_count')


    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'duration')


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)


    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'lessons_count', 'lessons')


    def get_lessons_count(self, obj):
        return obj.lessons.count()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user
