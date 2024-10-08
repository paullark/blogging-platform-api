from rest_framework import permissions
from django.urls import re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Blogging platform",
        default_version="v1",
        description="Платформа для регистрации пользователей, создания, просмотра и оценки статей",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

yasg_urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
