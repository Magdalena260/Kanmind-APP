
from django.contrib.auth.models import User
from django.db import models

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board, Comment, Task

from .permissions import (
    IsBoardMember,
    IsBoardOwner,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
    UserSerializer,
)


class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsBoardOwner()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return BoardUpdateSerializer

        return BoardDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()


class EmailCheckView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        email = self.request.query_params.get("email")

        if not email or not email.strip():
            raise ValidationError({
                "email": "Email address is required."
            })

        return generics.get_object_or_404(
            User,
            email=email.strip(),
        )


class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            assignee=self.request.user
        )


class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            reviewer=self.request.user
        )


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]
        self.check_object_permissions(self.request, board)
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                IsTaskCreatorOrBoardOwner(),
            ]

        return [IsAuthenticated(), IsBoardMember()]


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        task = self.get_task()
        return task.comments.all().order_by("created_at")

    def get_task(self):
        task = generics.get_object_or_404(
            Task,
            pk=self.kwargs["task_id"],
        )
        self.check_object_permissions(self.request, task)
        return task

    def perform_create(self, serializer):
        serializer.save(
            task=self.get_task(),
            author=self.request.user,
        )


class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
        IsCommentAuthor,
    ]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        )
