from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from dashboard.advanced_models import CameraAdvanced, AnalyticsSnapshot
from .serializers import CameraAdvancedSerializer, AnalyticsSnapshotSerializer
from .pagination import StandardResultsSetPagination

# مدیریت CameraAdvanced
# ويرايش تنظيمات پردازش وآناليتيكس
# قابلیت Filtering, Search, Ordering, Pagination
class CameraConfigViewSet(viewsets.ModelViewSet):
    # داده هایی که قراره نمایش داده بشه رو نشون میده
    queryset = CameraAdvanced.objects.all()
    # مشخص میکنه چطوری داده هارو به JSON تبدیل کنه تا در API یرگرده
    serializer_class = CameraAdvancedSerializer
    # مشخص میکنه چه ابزارهایی برای فیلتر و جستجو و مرتب سازی استفاده بشه
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # اجازه میده با URL مثل camera__name فیلتر کنه
    filterset_fields = ['camera__name']
    # امکان جستجو متن آزاد میده
    search_fields = ['camera__name']
    # مشخص میکنه با چه فیلدی مرتب بشه
    ordering_fields = ['created_at', 'updated_at']
    # پیش فرض روی created_at نزولی هست
    ordering = ['-created_at']
    # محدود کردن تعداد داده در هر صفحه مثلا ما اینجا ۱۰ تا داریم
    pagination_class = StandardResultsSetPagination


    # detail = True یعنی روی یک آیتم خاص اعمال میشه
    # @action اجازه میده یک مسیر API سفارشی برای هر رکورد بسازیم
    # این اکشن تنظیمات پردازش رو بروز میکنه
    @action(detail=True, methods=['POST'])
    def update_processing_config(self, request, pk=None):
        camera_adv = self.get_object()
        new_config = request.data.get("processing_config")
        if not new_config:
            return Response({"error": "processing_config is required"}, status=400)
        camera_adv.processing_config = new_config
        camera_adv.save()
        return Response({"status": "success", "processing_config": camera_adv.processing_config})

    # این اکشن تنظیمات آنالیتیکس رو بروز میکنه
    @action(detail=True, methods=['POST'])
    def update_analytics_settings(self, request, pk=None):
        camera_adv = self.get_object()
        new_settings = request.data.get("analytics_settings")
        if not new_settings:
            return Response({"error": "analytics_settings is required"}, status=400)
        camera_adv.analytics_settings = new_settings
        camera_adv.save()
        return Response({"status": "success", "analytics_settings": camera_adv.analytics_settings})

    # این اکشن تنطیمات کامل یک دوربین رو نشون میده
    # بدون تغییر داده فقط برمیگردونه
    @action(detail=True, methods=['GET'])
    def full_config(self, request, pk=None):
        camera_adv = self.get_object()
        serializer = self.get_serializer(camera_adv)
        return Response(serializer.data)


# مشاهده وفيلتر كردن snapshots دوربين هاى بيشرفته
class AnalyticsSnapshotViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsSnapshot.objects.all().order_by('-timestamp')
    serializer_class = AnalyticsSnapshotSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['camera_adv', 'timestamp']
    search_fields = ['camera_adv__camera__name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    pagination_class = StandardResultsSetPagination
