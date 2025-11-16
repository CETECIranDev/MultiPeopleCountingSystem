# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CameraViewSet, 
    PeopleCountViewSet, 
    AnomalyEventViewSet,
    AnalyticsSummaryView,
    AnalyticsHourlyReportView,
    AnalyticsTrendsView
)

router = DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'people-counts', PeopleCountViewSet)
router.register(r'anomalies', AnomalyEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Analytics endpoints
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('analytics/hourly-report/', AnalyticsHourlyReportView.as_view(), name='analytics-hourly'),
    path('analytics/trends/', AnalyticsTrendsView.as_view(), name='analytics-trends'),
    
    path('api-auth/', include('rest_framework.urls')),
]