from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """Journalist permissions"""
    def has_permission(self, request, view):
        return request.user.role == 'journalist'


class IsEditor(BasePermission):
    """Editor permissions"""
    def has_permission(self, request, view):
        return request.user.role == 'editor'


class IsReader(BasePermission):
    """Reader permissions"""
    def has_permission(self, request, view):
        return request.user.role == 'reader'