from django.contrib.postgres import serializers
from .models import Course, Lesson
from .validators import validate_youtube_link
from ..users.models import Payment


class LessonSerializer(serializers.ModelSerializer):
    material_link = serializers.URLField(validators=[validate_youtube_link])

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'duration', 'material_link')  # добавил material_link в поля

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'lessons_count', 'lessons', 'is_subscribed')

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.subscriptions.filter(user=request.user).exists()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
