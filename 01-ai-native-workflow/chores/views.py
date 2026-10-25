from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    """Placeholder home page."""
    return HttpResponse("<h1>Shared Household Chores</h1>")

