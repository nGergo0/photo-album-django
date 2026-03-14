from django.urls import path
from . import views

urlpatterns = [
    path('health/ready/', views.health_ready, name='health_ready'),
    path('', views.photo_list, name='photo_list'),
    path('photo/<int:pk>/', views.photo_detail, name='photo_detail'),
    path('upload/', views.photo_upload, name='photo_upload'),
    path('delete/<int:pk>/', views.photo_delete, name='photo_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]