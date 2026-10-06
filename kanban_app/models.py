from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True,
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        null=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        null=True,
        blank=True,
    )

    due_date = models.DateField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]