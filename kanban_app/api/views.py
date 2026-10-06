from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board

from .serializers import BoardSerializer