from django.urls import path

from .views import (
    AssignedToMeView,
    BoardDetailView,
    BoardListView,
    EmailCheckView,
)


urlpatterns = [
    path(
        "boards/",
        BoardListView.as_view(),
        name="board-list",
    ),
    path(
        "boards/<int:pk>/",
        BoardDetailView.as_view(),
        name="board-detail",
    ),
    path(
        "email-check/",
        EmailCheckView.as_view(),
        name="email-check",
    ),
    path(
        "tasks/assigned-to-me/",
        AssignedToMeView.as_view(),
        name="tasks-assigned-to-me",
    ),
]