from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'journalist'


class IsEditor(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'editor'


class IsReader(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'reader'