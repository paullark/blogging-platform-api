from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Subscription
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # переопределение админ-форм
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": ("birth_date", "photo", "about"),
            },
        ),
    )


admin.site.register(Subscription)
