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
    class Meta:
        model = Task