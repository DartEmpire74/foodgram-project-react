from rest_framework import permissions


class UserAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'me' in request.path.split('/'):
            return request.user and request.user.is_authenticated
        return True
