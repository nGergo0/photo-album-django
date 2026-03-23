from django.urls import path

from . import api_views


urlpatterns = [
    path('health/ready/', api_views.HealthReadyAPIView.as_view(), name='api_health_ready'),
    path('photos/', api_views.PhotoListCreateAPIView.as_view(), name='api_photo_list_create'),
    path('photos/<int:pk>/', api_views.PhotoDetailAPIView.as_view(), name='api_photo_detail'),
    path('auth/register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('auth/token/', api_views.TokenLoginAPIView.as_view(), name='api_token_login'),
    path('auth/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
]
