
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


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = getattr(obj, "board", obj)

        return (
            board.owner == request.user
            or board.members.filter(
                pk=request.user.pk
            ).exists()
        )
