# dashboard/models.py
from django.db import models
#from django.contrib.gis.db import models as gis_models

# dashboard/models.py

# به جای:
# from django.contrib.gis.db import models as gis_models

# از این استفاده کنید:
from django.db import models

class Camera(models.Model):
    CAMERA_TYPES = [
        ('entrance', 'ورودی'),
        ('exit', 'خروجی'),
        ('general', 'عمومی'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام دوربین')
    # location = gis_models.PointField(verbose_name='موقعیت جغرافیایی', null=True, blank=True)  # حذف
    location_name = models.CharField(max_length=255, verbose_name='نام موقعیت', blank=True)
    latitude = models.FloatField(null=True, blank=True, verbose_name='عرض جغرافیایی')
    longitude = models.FloatField(null=True, blank=True, verbose_name='طول جغرافیایی')
    stream_url = models.URLField(verbose_name='آدرس استریم')
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPES, default='general')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    calibration_data = models.JSONField(null=True, blank=True, verbose_name='داده‌های کالیبراسیون')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دوربین'
        verbose_name_plural = 'دوربین‌ها'
        indexes = [
            models.Index(fields=['is_active', 'camera_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_camera_type_display()})"
class PeopleCount(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, verbose_name='دوربین')
    count_in = models.IntegerField(default=0, verbose_name='تعداد ورود')
    count_out = models.IntegerField(default=0, verbose_name='تعداد خروج')
    total_inside = models.IntegerField(default=0, verbose_name='مجموع حاضر')
    density_map = models.JSONField(null=True, blank=True, verbose_name='نقشه تراکم')
    frame_data = models.JSONField(null=True, blank=True, verbose_name='داده‌های فریم')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')
    
    class Meta:
        verbose_name = 'شمارش افراد'
        verbose_name_plural = 'شمارش افراد'
        indexes = [
            models.Index(fields=['timestamp', 'camera']),
            models.Index(fields=['camera', 'timestamp']),
        ]
        ordering = ['-timestamp']

class AnomalyEvent(models.Model):
    ABNORMAL_TYPES = [
        ('congestion', 'تراکم غیرعادی'),
        ('loitering', 'توقف طولانی'),
        ('wrong_direction', 'حرکت مخالف'),
        ('crowd_gathering', 'تجمع ناگهانی'),
        ('no_movement', 'عدم حرکت'),
    ]
    
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, verbose_name='دوربین')
    anomaly_type = models.CharField(max_length=20, choices=ABNORMAL_TYPES, verbose_name='نوع ناهنجاری')
    track_id = models.IntegerField(null=True, blank=True, verbose_name='شناسه ردیابی')
    confidence = models.FloatField(verbose_name='میزان اطمینان')
    frame_data = models.JSONField(verbose_name='داده‌های فریم')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')
    is_resolved = models.BooleanField(default=False, verbose_name='رفع شده')
    
    class Meta:
        verbose_name = 'رویداد غیرعادی'
        verbose_name_plural = 'رویدادهای غیرعادی'
        indexes = [
            models.Index(fields=['timestamp', 'anomaly_type']),
            models.Index(fields=['is_resolved', 'camera']),
        ]
        ordering = ['-timestamp']

class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='کلید')
    value = models.JSONField(verbose_name='مقدار')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تنظیمات سیستم'
        verbose_name_plural = 'تنظیمات سیستم'