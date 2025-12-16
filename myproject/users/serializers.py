from .models import User
from ..lms import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone', 'city', 'avatar']
        read_only_fields = ['email']