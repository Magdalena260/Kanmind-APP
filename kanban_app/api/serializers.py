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

    ticket_count = serializers.IntegerField(
        source="tasks.count",
        read_only=True,
    )

    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


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
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
            "created_by",
        ]
        read_only_fields = [
            "created_by",
        ]

    def validate(self, attrs):
        board = attrs.get("board")

        if self.instance and board and board != self.instance.board:
            raise serializers.ValidationError(
                {"board": "Board cannot be changed."}
            )

        if board is None and self.instance:
            board = self.instance.board

        assignee = attrs.get("assignee")
        reviewer = attrs.get("reviewer")

        if assignee and assignee not in board.members.all():
            raise serializers.ValidationError(
                {"assignee_id": "Assignee must be a board member."}
            )

        if reviewer and reviewer not in board.members.all():
            raise serializers.ValidationError(
                {"reviewer_id": "Reviewer must be a board member."}
            )

        return attrs



    class BoardDetailSerializer(serializers.ModelSerializer):
     members = UserSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
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