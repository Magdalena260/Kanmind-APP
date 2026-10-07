from django.db import models

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board

from .permissions import IsBoardOwner
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
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