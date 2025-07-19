from django.urls import path
from . import views

urlpatterns = [
    path('', views.standings_overview, name='standings_overview')
]