from django.urls import path
from . import views

urlpatterns = [
    path('', views.standings_overview, name='standings_overview'),
    path('stats/', views.team_roster_stats, name='roster_stats'),
]