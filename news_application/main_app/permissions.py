from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """Journalist permissions"""
    def has_permission(self, request, view):
        return (
            request.user.role == 'journalist'
            or request.user.groups.filter(
                name='Journalist'
            ).exists()
        )


class IsEditor(BasePermission):
    """Editor permissions"""
    def has_permission(self, request, view):
        return (
            request.user.role == 'editor'
            or request.user.groups.filter(
                name='Editor'
            ).exists()
        )


class IsReader(BasePermission):
    """Reader permissions"""
    def has_permission(self, request, view):
        return (
            request.user.role == 'reader'
            or request.user.groups.filter(
                name='Reader'
            ).exists()
        )
