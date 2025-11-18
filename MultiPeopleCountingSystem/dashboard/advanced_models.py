from django.db import models
from dashboard.models import Camera

class CameraAdvanced(models.Model):
    camera = models.OneToOneField(Camera, on_delete=models.CASCADE, verbose_name='دوربین پایه')
    processing_config = models.JSONField(default=dict, verbose_name='تنظیمات پردازش')
    analytics_settings = models.JSONField(default=dict, verbose_name='تنظیمات آنالیتیکس')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'دوربین پیشرفته'
        verbose_name_plural = 'دوربین‌های پیشرفته'

    def __str__(self):
        return f"Advanced {self.camera.name}"


class AnalyticsSnapshot(models.Model):
    camera_adv = models.ForeignKey(CameraAdvanced, on_delete=models.CASCADE, related_name='snapshots',verbose_name='دوربین پیشرفته')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')
    snapshot_data = models.JSONField(default=dict, verbose_name='داده‌های آنالیتیکس')

    class Meta:
        verbose_name = 'آنالیتیکس Snapshot'
        verbose_name_plural = 'آنالیتیکس Snapshotها'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Snapshot {self.id} - {self.camera_adv.camera.name}"
