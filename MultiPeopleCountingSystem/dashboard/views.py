# dashboard/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Avg
from .models import Camera, PeopleCount, AnomalyEvent

def dashboard_home(request):
    """صفحه اصلی داشبورد"""
    cameras = Camera.objects.filter(is_active=True)
    
    # آمار سریع
    total_cameras = Camera.objects.count()
    active_cameras = cameras.count()
    active_anomalies = AnomalyEvent.objects.filter(is_resolved=False).count()
    
    # آخرین داده‌های شمارش
    recent_counts = PeopleCount.objects.select_related('camera').order_by('-timestamp')[:10]
    
    # آمار امروز
    today = timezone.now().date()
    today_stats = PeopleCount.objects.filter(
        timestamp__date=today
    ).aggregate(
        total_entries=Sum('count_in'),
        total_exits=Sum('count_out')
    )
    
    context = {
        'total_cameras': total_cameras,
        'active_cameras': active_cameras,
        'active_anomalies': active_anomalies,
        'today_entries': today_stats['total_entries'] or 0,
        'today_exits': today_stats['total_exits'] or 0,
        'recent_counts': recent_counts,
        'cameras': cameras,
    }
    return render(request, 'dashboard/home.html', context)

def camera_list(request):
    """لیست تمام دوربین‌ها"""
    cameras = Camera.objects.all()
    return render(request, 'dashboard/camera_list.html', {'cameras': cameras})

def camera_detail(request, camera_id):
    """جزئیات دوربین خاص"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    # داده‌های اخیر این دوربین
    recent_counts = PeopleCount.objects.filter(camera=camera).order_by('-timestamp')[:20]
    anomalies = AnomalyEvent.objects.filter(camera=camera, is_resolved=False)[:10]
    
    # آمار امروز این دوربین
    today = timezone.now().date()
    today_stats = PeopleCount.objects.filter(
        camera=camera,
        timestamp__date=today
    ).aggregate(
        total_entries=Sum('count_in'),
        total_exits=Sum('count_out'),
        avg_density=Avg('total_inside')
    )
    
    context = {
        'camera': camera,
        'recent_counts': recent_counts,
        'anomalies': anomalies,
        'today_entries': today_stats['total_entries'] or 0,
        'today_exits': today_stats['total_exits'] or 0,
        'avg_density': round(today_stats['avg_density'] or 0, 2),
    }
    return render(request, 'dashboard/camera_detail.html', context)

def analytics_dashboard(request):
    """صفحه آنالیتیکس"""
    # داده‌های برای نمودارها
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    daily_counts = PeopleCount.objects.filter(
        timestamp__date__gte=week_ago
    ).extra({'date': "date(timestamp)"}).values('date').annotate(
        total_in=Sum('count_in'),
        total_out=Sum('count_out')
    ).order_by('date')
    
    context = {
        'daily_counts': list(daily_counts),
        'start_date': week_ago,
        'end_date': today,
    }
    return render(request, 'dashboard/analytics.html', context)

def reports_view(request):
    """صفحه گزارش‌ها"""
    return render(request, 'dashboard/reports.html')

# API views برای داده‌های real-time
def camera_realtime_data(request, camera_id):
    """داده‌های real-time برای دوربین (API)"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    recent_data = PeopleCount.objects.filter(
        camera=camera
    ).order_by('-timestamp').first()
    
    if recent_data:
        data = {
            'camera_id': camera.id,
            'camera_name': camera.name,
            'count_in': recent_data.count_in,
            'count_out': recent_data.count_out,
            'total_inside': recent_data.total_inside,
            'timestamp': recent_data.timestamp.isoformat(),
        }
    else:
        data = {
            'camera_id': camera.id,
            'camera_name': camera.name,
            'count_in': 0,
            'count_out': 0,
            'total_inside': 0,
            'timestamp': timezone.now().isoformat(),
        }
    
    return JsonResponse(data)