# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('cameras/', views.camera_list, name='camera_list'),
    path('cameras/<int:camera_id>/', views.camera_detail, name='camera_detail'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
]