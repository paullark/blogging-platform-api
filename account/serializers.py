from rest_framework import serializers
from django.conf import settings
from .models import CustomUser

from .services.subscription_service import subscribe_user
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('account_logger')


class UserBaseSerializer(serializers.ModelSerializer):
    user_rating = serializers.CharField(source='get_user_rating',
                                        read_only=True)
    article_count = serializers.IntegerField(source='articles.count',
                                             read_only=True)
    is_subscription = serializers.SerializerMethodField('is_user_in_subscriptions')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_rating', 'article_count', 'is_subscription']

    def is_user_in_subscriptions(self, user):
        request = self.context.get('request')
        try:
            my_user = request.user
            if user in my_user.subscriptions.all():
                return True
        except AttributeError:
            LOGGER.error(f'request.user not found')
        return False


class UserListSerializer(UserBaseSerializer):
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['url']


class UserDetailSerializer(UserBaseSerializer):
    subscription_count = serializers.IntegerField(source='subscriptions.count',
                                                  read_only=True)
    subscriber_count = serializers.IntegerField(source='subscribers.count',
                                                read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            'first_name',
            'last_name',
            'email',
            'birth_date',
            'date_joined',
            'photo',
            'subscription_count',
            'subscriber_count'
        ]


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email', 'birth_date', 'photo'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
