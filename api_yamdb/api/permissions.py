# api_yamdb/api/permissions.py
from rest_framework import permissions


class AdminPermission(permissions.BasePermission):
    """Права доступа администратора или суперпользователя."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права доступа к спискам произведений, жанров и категорий."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        ))


class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """Права доступа к отзывам и комментариям."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)
