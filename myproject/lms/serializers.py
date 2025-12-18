from django.contrib.auth.models import User
from django.contrib.postgres import serializers

from .models import Course, Lesson
from .validators import validate_youtube_link
from ..users.models import Payment


class LessonSerializer(serializers.ModelSerializer):
    material_link = serializers.URLField(validators=[validate_youtube_link])
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'duration')


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)


    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'lessons_count', 'lessons')

        def get_is_subscribed(self, obj):
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
            return obj.subscriptions.filter(user=user).exists()


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
