from django.contrib.auth.models import User

from rest_framework import serializers

from kanban_app.models import Board, Comment, Task


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(
        source="first_name",
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(
        source="members.count",
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "owner",
            "members",
        ]


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    source="assignee",
    write_only=True,
    required=False,
    allow_null=True,
)

    reviewer_id = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    source="reviewer",
    write_only=True,
    required=False,
    allow_null=True,
)
    
    comments_count = serializers.IntegerField(
        source="comments.count",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "author",
            "content",
            "created_at",
        ]