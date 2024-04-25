from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет только авторам
    рецептов редактировать или удалять их.
    Разрешает чтение всем пользователям.
    Разрешает создание только аутентифицированным пользователям.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class UserAccessPermission(permissions.BasePermission):
    """
    Предоставляет доступ к /users/me/ только
    аутентифицированным пользователям.
    Доступ к /users/{id}/ предоставляется всем пользователям.
    """

    def has_permission(self, request, view):
        if 'me' in request.path.split('/'):
            return request.user and request.user.is_authenticated
        return True
