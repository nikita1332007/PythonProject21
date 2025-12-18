from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='moderators').exists()

class IsModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_moder = request.user.groups.filter(name='moderators').exists()
        if request.method in ['POST', 'DELETE']:
            return not is_moder and request.user.is_authenticated
        return request.user.is_authenticated

class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        return obj.owner == request.user