
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase

from kanban_app.models import Board, Comment, Task


class BoardModelTest(TestCase):
    def test_board_creation(self):
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="Test12345!",
        )
        board = Board.objects.create(
            title="Mein Testboard",
            owner=user,
        )
        self.assertEqual(board.title, "Mein Testboard")
        self.assertEqual(board.owner, user)


class BoardApiTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="Test12345!"
        )
        self.other = User.objects.create_user(
            username="other", password="Test12345!"
        )
        self.board = Board.objects.create(
            title="Testboard", owner=self.owner
        )

    def test_owner_can_view_board(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_view_board(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_list_boards(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_other_user_sees_no_boards(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class TaskApiTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="taskowner")
        self.other = User.objects.create_user(username="taskother")
        self.board = Board.objects.create(
            title="Taskboard", owner=self.owner
        )
        self.board.members.add(self.owner)
        self.task = Task.objects.create(
            board=self.board,
            created_by=self.owner,
            title="Testtask",
            description="Beschreibung",
            status="to-do",
            priority="high",
            due_date=date(2026, 10, 15),
        )

    def test_owner_can_view_task(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 200)

    def test_other_cannot_view_task(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_update_task(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/",
            {"status": "in-progress"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_cannot_change_task_board(self):
        second_board = Board.objects.create(
            title="Anderes Board", owner=self.owner
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/",
            {"board": second_board.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_owner_can_delete_task(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 204)


class CommentApiTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="commentowner"
        )
        self.board = Board.objects.create(
            title="Board", owner=self.owner
        )
        self.task = Task.objects.create(
            board=self.board,
            created_by=self.owner,
            title="Task",
            description="Test",
            status="to-do",
            priority="low",
            due_date=date(2026, 10, 15),
        )
        self.comment = Comment.objects.create(
            task=self.task,
            author=self.owner,
            content="Hallo!",
        )

    def test_owner_can_list_comments(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            f"/api/tasks/{self.task.id}/comments/"
        )
        self.assertEqual(response.status_code, 200)

    def test_owner_can_create_comment(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f"/api/tasks/{self.task.id}/comments/",
            {"content": "Neuer Kommentar"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_author_can_delete_comment(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{self.comment.id}/"
        )
        self.assertEqual(response.status_code, 204)
