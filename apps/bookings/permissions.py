from rest_framework import permissions


# https://testdriven.io/blog/custom-permission-classes-drf/
class TestPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class ReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class AllowListingOwnerOrBookingUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.listing.owner == request.user or obj.user == request.user
