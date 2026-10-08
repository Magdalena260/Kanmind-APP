
from django.contrib.auth.models import User

from rest_framework import serializers

from kanban_app.models import Board, Comment, Task


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]

    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username


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
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True,
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
        ]

    def validate(self, attrs):
        board = attrs.get("board")
        if self.instance:
            self.check_board_change(board)
            board = board or self.instance.board
        self.check_board_user(attrs, board, "assignee")
        self.check_board_user(attrs, board, "reviewer")
        return attrs

    def check_board_change(self, board):
        if board and board != self.instance.board:
            raise serializers.ValidationError(
                {"board": "Board cannot be changed."}
            )

    def check_board_user(self, attrs, board, field):
        user = attrs.get(field)
        if user and not board.members.filter(pk=user.pk).exists():
            raise serializers.ValidationError({
                f"{field}_id": "User must be a board member."
            })


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True,
    )
    members = UserSerializer(
        many=True,
        read_only=True,
    )
    tasks = TaskSerializer(
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
            "tasks",
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(
        source="owner",
        read_only=True,
    )
    members_data = UserSerializer(
        source="members",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "owner_data",
            "members_data",
        ]
        extra_kwargs = {
            "members": {"write_only": True},
        }


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
        read_only_fields = [
            "created_at",
            "author",
        ]

    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username
