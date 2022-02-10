from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    user_rating = serializers.SerializerMethodField('get_user_rating')

    @staticmethod
    def get_user_rating(foo):
        return foo.get_user_rating()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'birth_date', 'photo', 'user_rating']


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'birth_date', 'photo']
