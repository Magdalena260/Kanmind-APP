
from django.contrib.auth.models import User
from django.test import TestCase

from kanban_app.models import Board


class BoardModelTest(TestCase):
    def test_board_creation(self):
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="Test12345!"
        )
        board = Board.objects.create(
            title="Mein Testboard",
            owner=user
        )

        self.assertEqual(board.title, "Mein Testboard")
        self.assertEqual(board.owner, user)
