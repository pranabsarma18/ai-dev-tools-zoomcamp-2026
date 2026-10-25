from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("households/create/", views.create_household, name="create_household"),
    path("households/<int:pk>/", views.household_detail, name="household_detail"),
    path("households/<int:pk>/board/", views.board_view, name="board"),
    path("households/<int:pk>/chores/", views.chore_list, name="chore_list"),
    path("households/<int:pk>/chores/create/", views.chore_create, name="chore_create"),
    path("households/<int:pk>/chores/<int:chore_pk>/edit/", views.chore_edit, name="chore_edit"),
    path("households/<int:pk>/chores/<int:chore_pk>/delete/", views.chore_delete, name="chore_delete"),
    path("households/<int:pk>/chores/<int:chore_pk>/complete/", views.complete_chore, name="complete_chore"),
    path("households/<int:pk>/completions/<int:completion_pk>/verify/", views.verify_completion, name="verify_completion"),
    path("join/", views.join_household, name="join_household"),
]
