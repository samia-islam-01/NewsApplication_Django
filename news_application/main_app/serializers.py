from rest_framework import serializers

from .models import (
    Article,
    Newsletter,
    Publisher,
    CustomUser
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'role'
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Publisher serializer"""
    class Meta:
        model = Publisher
        fields = '__all__'
    class Meta:
        model = Publisher
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    """Newsletter serializer"""
    class Meta:
        model = Newsletter
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """Article serializer"""
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'