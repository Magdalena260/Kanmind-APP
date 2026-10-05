from rest_framework import serializers

from kanban_app.models import Board, Comment, Task


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