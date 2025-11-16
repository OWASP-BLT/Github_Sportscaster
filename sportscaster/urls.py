"""
URL configuration for sportscaster app
"""
from django.urls import path
from . import views

app_name = 'sportscaster'

urlpatterns = [
    # Web views
    path('', views.index, name='index'),
    path('channel/<int:channel_id>/', views.channel_view, name='channel'),
    
    # API endpoints
    path('api/channels/', views.api_channels, name='api_channels'),
    path('api/channel/<int:channel_id>/events/', views.api_channel_events, name='api_channel_events'),
    path('api/channel/<int:channel_id>/leaderboard/', views.api_leaderboard, name='api_leaderboard'),
    path('api/test-commentary/', views.api_test_commentary, name='api_test_commentary'),
]
