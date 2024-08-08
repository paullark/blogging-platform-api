from rest_framework import permissions


class IsPublishAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на изменение опубликованных статей
    только для авторов и на чтение для всех пользователей
    """

    message = "Edit allowed for author only"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsDraftAuthor(permissions.BasePermission):
    """Разрешение на чтение и изменение черновиков только для авторов"""

    message = "Draft read and edit allowed for author only"

    def has_permission(self, request, view):
        if request.GET.get("filter") != "draft":
            return True
        username = request.GET.get("username")
        if request.user.username == username:
            return True
        return bool(not username and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.status != "draft" or request.user == obj.author


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на создание комментариев только к опубликованным статьям,
    изменение для автора комментария, чтение для всех пользователей
    """

    message = "Edit allowed for author only"

    def has_permission(self, request, view):
        return bool(view.article and view.article.status != "draft")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsArticleContentAuthor(permissions.BasePermission):
    """Изменение контента только для автора статьи"""

    message = "Edit allowed for author only"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(view.article and view.article.author == request.user)
