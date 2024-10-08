from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from courses.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Subscription
        fields = (
            'user',
            'course',
            'is_valid'
        )
