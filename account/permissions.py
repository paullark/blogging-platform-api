from rest_framework import permissions


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование профиля для владельца и
    просмотр для остальных
    """
    message = 'Edit allowed for owner only'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
