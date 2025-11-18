# api/serializers.py
from rest_framework import serializers
from dashboard.models import Camera, PeopleCount, AnomalyEvent
from dashboard.advanced_models import CameraAdvanced,AnalyticsSnapshot

class CameraSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Camera
        fields = '__all__'
    
    def get_status(self, obj):
        return 'active' if obj.is_active else 'inactive'
    
    def get_recent_activity(self, obj):
        recent = PeopleCount.objects.filter(camera=obj).order_by('-timestamp').first()
        if recent:
            return {
                'last_count': recent.total_inside,
                'last_update': recent.timestamp
            }
        return None

class PeopleCountSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    camera_type = serializers.CharField(source='camera.camera_type', read_only=True)
    
    class Meta:
        model = PeopleCount
        fields = '__all__'

class AnomalyEventSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    camera_location = serializers.CharField(source='camera.location_name', read_only=True)
    
    class Meta:
        model = AnomalyEvent
        fields = '__all__'

class AnalyticsSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_entries = serializers.IntegerField()
    total_exits = serializers.IntegerField()
    peak_hour = serializers.CharField()
    avg_density = serializers.FloatField()

class HourlyReportSerializer(serializers.Serializer):
    hour = serializers.CharField()
    entries = serializers.IntegerField()
    exits = serializers.IntegerField()
    records = serializers.IntegerField()

class CameraAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraAdvanced
        fields = '__all__'

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'