# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .advanced_views import CameraConfigViewSet,AnalyticsSnapshotViewSet
from .views import (
    CameraViewSet, 
    PeopleCountViewSet, 
    AnomalyEventViewSet,
    AnalyticsSummaryView,
    AnalyticsHourlyReportView,
    AnalyticsTrendsView
)

router = DefaultRouter()
# Main
router.register(r'cameras', CameraViewSet)
router.register(r'people-counts', PeopleCountViewSet)
router.register(r'anomalies', AnomalyEventViewSet)
# Advanced
router.register(r'camera-advanced', CameraConfigViewSet)
router.register(r'analytics-snapshots', AnalyticsSnapshotViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Analytics endpoints
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('analytics/hourly-report/', AnalyticsHourlyReportView.as_view(), name='analytics-hourly'),
    path('analytics/trends/', AnalyticsTrendsView.as_view(), name='analytics-trends'),
    
    path('api-auth/', include('rest_framework.urls')),
]