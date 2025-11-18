# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Avg
from .serializers import *
from dashboard.models import *

# مدیریت و API دوربین‌ها
# این ویو برای CRUD کامل روی Camera است
# ليست, اضافه كردن، ويرايش، حذف دوربينها
# عمليات ويژه: كاليبراسيون و داده Real-time
class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'camera_type']
    
    @action(detail=True, methods=['post'])
    def calibrate(self, request, pk=None):
        """کالیبراسیون دوربین"""
        camera = self.get_object()
        return Response({
            'status': 'calibration started', 
            'camera': camera.name,
            'message': 'کالیبراسیون با موفقیت آغاز شد'
        })
    
    @action(detail=True, methods=['get'])
    # داده بلادرنگ آخرین ۵ دقیقه
    def realtime_data(self, request, pk=None):
        """داده‌های real-time دوربین"""
        camera = self.get_object()
        recent_data = PeopleCount.objects.filter(
            camera=camera, 
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        ).order_by('-timestamp').first()
        
        if recent_data:
            serializer = PeopleCountSerializer(recent_data)
            return Response(serializer.data)
        return Response({
            'message': 'No recent data available',
            'camera_id': camera.id,
            'camera_name': camera.name
        })


# فقط خواندن داده‌های شمارش افراد
# این ویوست برای صفحه گزارش و نمودارها ضروریه
# ليست داده هاى شمارش افراد
# فيلتر بر اساس تاريخ و دوربين
class PeopleCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PeopleCount.objects.all().order_by('-timestamp')
    serializer_class = PeopleCountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['camera', 'timestamp']
    
    def get_queryset(self):
        queryset = PeopleCount.objects.all()
        
        # فیلترهای اختیاری
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        camera_id = self.request.query_params.get('camera_id')
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
            
        return queryset.order_by('-timestamp')


# جایگزینی AnalyticsViewSet با APIView ساده‌تر
class AnalyticsSummaryView(APIView):
    def get(self, request):
        """خلاصه آمار سیستم"""
        today = timezone.now().date()
        
        # محاسبه آمار امروز
        today_stats = PeopleCount.objects.filter(
            timestamp__date=today
        ).aggregate(
            total_entries=Sum('count_in'),
            total_exits=Sum('count_out'),
            avg_density=Avg('total_inside')
        )
        
        summary = {
            'total_cameras': Camera.objects.count(),
            'active_cameras': Camera.objects.filter(is_active=True).count(),
            'today_entries': today_stats['total_entries'] or 0,
            'today_exits': today_stats['total_exits'] or 0,
            'avg_density_today': round(today_stats['avg_density'] or 0, 2),
            'active_anomalies': AnomalyEvent.objects.filter(is_resolved=False).count(),
            'last_update': timezone.now().isoformat()
        }
        
        return Response(summary)

# گزارش ساعتی که برای نمودار خطی یا BarChart می‌باشد
class AnalyticsHourlyReportView(APIView):
    def get(self, request):
        """گزارش ساعتی"""
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        camera_id = request.query_params.get('camera_id')
        
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # فیلتر بر اساس دوربین اگر مشخص شده
            if camera_id:
                counts = PeopleCount.objects.filter(
                    camera_id=camera_id,
                    timestamp__date=target_date
                )
            else:
                counts = PeopleCount.objects.filter(timestamp__date=target_date)
            
            # تولید داده‌های ساعتی
            hourly_data = []
            for hour in range(24):
                hour_start = timezone.datetime.combine(target_date, timezone.time(hour, 0))
                hour_end = hour_start + timedelta(hours=1)
                
                hour_counts = counts.filter(
                    timestamp__range=[hour_start, hour_end]
                ).aggregate(
                    total_in=Sum('count_in'),
                    total_out=Sum('count_out'),
                    record_count=Count('id')
                )
                
                hourly_data.append({
                    'hour': f"{hour:02d}:00",
                    'entries': hour_counts['total_in'] or 0,
                    'exits': hour_counts['total_out'] or 0,
                    'records': hour_counts['record_count']
                })
            
            return Response({
                'date': date_str,
                'camera_id': camera_id,
                'hourly_data': hourly_data
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# نمودار ترند ۷ روز گذشته
class AnalyticsTrendsView(APIView):
    def get(self, request):
        """داده‌های ترند"""
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        trends = PeopleCount.objects.filter(
            timestamp__date__range=[start_date, end_date]
        ).extra({'date': "date(timestamp)"}).values('date').annotate(
            total_in=Sum('count_in'),
            total_out=Sum('count_out'),
            avg_density=Avg('total_inside'),
            record_count=Count('id')
        ).order_by('date')
        
        return Response(list(trends))

# ليست رويدادهاى غير عادى
# قابليت علامت كذارى به عنوان حل شده
class AnomalyEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnomalyEvent.objects.all().order_by('-timestamp')
    serializer_class = AnomalyEventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['camera', 'anomaly_type', 'is_resolved']
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """علامت گذاری رویداد به عنوان حل شده"""
        anomaly = self.get_object()
        anomaly.is_resolved = True
        anomaly.save()
        
        return Response({
            'status': 'success',
            'message': 'رویداد به عنوان حل شده علامت گذاری شد',
            'anomaly_id': anomaly.id
        })