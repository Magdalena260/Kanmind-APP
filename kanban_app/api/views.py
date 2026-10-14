from django.contrib.auth.models import User
from django.db.models import Count, Prefetch, Q

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


def boards_with_counts():
    return Board.objects.annotate(
        member_count=Count("members", distinct=True),
        ticket_count=Count("tasks", distinct=True),
        tasks_to_do_count=Count(
            "tasks",
            filter=Q(tasks__status="to-do"),
            distinct=True,
        ),
        tasks_high_prio_count=Count(
            "tasks",
            filter=Q(tasks__priority="high"),
            distinct=True,
        ),
    )


def tasks_with_counts():
    return Task.objects.select_related(
        "assignee",
        "reviewer",
        "board__owner",
    ).annotate(
        comments_count=Count("comments", distinct=True)
    )


class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return boards_with_counts().filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        board = boards_with_counts().get(pk=serializer.instance.pk)
        return Response(
            self.get_serializer(board).data,
            status=status.HTTP_201_CREATED,
        )


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        return Board.objects.select_related(
            "owner",
        ).prefetch_related(
            "members",
            Prefetch("tasks", queryset=tasks_with_counts()),
        )

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer


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
        return tasks_with_counts().filter(
            assignee=self.request.user
        )


class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return tasks_with_counts().filter(
            reviewer=self.request.user
        )


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]
        self.check_object_permissions(self.request, board)
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        task = tasks_with_counts().get(pk=serializer.instance.pk)
        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return tasks_with_counts()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.updated_task_response(instance.pk)

    def updated_task_response(self, task_id):
        task = tasks_with_counts().get(pk=task_id)
        return Response(self.get_serializer(task).data)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        task = self.get_task()
        return task.comments.select_related(
            "author"
        ).order_by("created_at")

    def get_task(self):
        task = generics.get_object_or_404(
            Task.objects.select_related("board__owner"),
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
        return Comment.objects.select_related(
            "author"
        ).filter(
            task_id=self.kwargs["task_id"]
        )