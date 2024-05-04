from rest_framework import permissions


class UserAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            'me' not in request.path.split('/') or (
                request.user and request.user.is_authenticated))
