from .models import CustomUser
from .services.mixins import PasswordsMatchValidationMixin
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger("account_logger")


class UserBaseSerializer(serializers.ModelSerializer):
    user_rating = serializers.IntegerField(source="get_user_rating", read_only=True)
    article_count = serializers.IntegerField(source="articles.count", read_only=True)
    is_subscription = serializers.SerializerMethodField(
        "is_user_in_subscriptions", read_only=True
    )

    class Meta:
        model = CustomUser
        fields = ["id", "username", "user_rating", "article_count", "is_subscription"]
        read_only_fields = ["id"]

    def is_user_in_subscriptions(self, user):
        """Проверяет, находится ли пользователь в подписках"""
        request = self.context.get("request")
        try:
            my_user = request.user
            if user in my_user.subscriptions.all():
                return True
        except AttributeError:
            LOGGER.error(f"request.user not found")
        return False


class UserListSerializer(UserBaseSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["url"]


class UserDetailUpdateSerializer(UserBaseSerializer):
    subscription_count = serializers.IntegerField(
        source="subscriptions.count", read_only=True
    )
    subscriber_count = serializers.IntegerField(
        source="subscribers.count", read_only=True
    )

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "date_joined",
            "photo",
            "subscription_count",
            "subscriber_count",
        ]
        read_only_fields = ["date_joined"]


class UserCreateSerializer(PasswordsMatchValidationMixin, serializers.ModelSerializer):
    password2 = serializers.CharField(
        required=True, label="Подтверждение пароля", write_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "photo",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        new_user = CustomUser(**validated_data)
        new_user.set_password(password)
        new_user.save()
        return new_user


class PasswordSetSerializer(PasswordsMatchValidationMixin, serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validate_data):
        instance.set_password(validate_data.get("password"))
        instance.save()
        return instance


class PasswordChangeSerializer(PasswordSetSerializer):
    old_password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data.get("old_password")):
            raise ValidationError("old password incorrect")
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance
