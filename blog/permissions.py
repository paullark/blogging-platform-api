from rest_framework import permissions


class IsPublishOrCommentAuthor(permissions.BasePermission):
    """
    Разрешение на изменение опубликованных статей и комментариев
    только для авторов и на чтение для всех пользователей
    """
    message = 'Edit allowed for author only'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsDraftAuthor(permissions.BasePermission):
    """Разрешение на чтение и изменение черновиков только для авторов"""
    message = 'Draft read and edit allowed for author only'

    def has_permission(self, request, view):
        if request.GET.get('filter') != 'draft':
            return True
        username = request.GET.get('username')
        if request.user.username == username:
            return True
        return bool(
            not username and
            request.user.is_authenticated
        )
