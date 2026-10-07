from rest_framework.permissions import BasePermission


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsTaskCreatorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user
            or obj.board.owner == request.user
        )
