from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Переопределение admin-формы создания пользователя"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('birth_date', 'photo')


class CustomUserChangeForm(UserChangeForm):
    """Переопределение admin-формы изменения пользователя"""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'photo']
