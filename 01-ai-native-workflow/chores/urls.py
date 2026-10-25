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
    path("join/", views.join_household, name="join_household"),
]
