# dashboard/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Camera, PeopleCount, AnomalyEvent, SystemConfig

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'camera_type', 'is_active', 'created_at', 'admin_actions']
    list_filter = ['camera_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    def admin_actions(self, obj):
        return format_html(
            '<a class="button" href="/admin/dashboard/camera/{}/change/">ویرایش</a> '
            '<a class="button" href="/api/cameras/{}/realtime-data/" style="background-color: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">مشاهده</a>',
            obj.id, obj.id
        )
    admin_actions.short_description = 'عملیات'

@admin.register(PeopleCount)
class PeopleCountAdmin(admin.ModelAdmin):
    list_display = ['camera', 'count_in', 'count_out', 'total_inside', 'timestamp']
    list_filter = ['camera', 'timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def has_add_permission(self, request):
        return False  # غیرفعال کردن افزودن دستی
    
    def has_change_permission(self, request, obj=None):
        return False  # غیرفعال کردن ویرایش دستی

@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ['camera', 'anomaly_type', 'confidence', 'timestamp', 'is_resolved', 'admin_actions']
    list_filter = ['anomaly_type', 'is_resolved', 'camera', 'timestamp']
    readonly_fields = ['timestamp']
    list_per_page = 20
    
    def admin_actions(self, obj):
        if not obj.is_resolved:
            return format_html(
                '<a class="button" href="/admin/dashboard/anomalyevent/{}/change/">ویرایش</a> '
                '<a class="button" style="background-color: #ff9800; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;" href="#" onclick="markResolved({})">حل شده</a>',
                obj.id, obj.id
            )
        return "حل شده"
    admin_actions.short_description = 'عملیات'
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'{updated} رویداد به عنوان حل شده علامت گذاری شد.')
    mark_resolved.short_description = "علامت گذاری رویدادهای انتخاب شده به عنوان حل شده"
    
    # تعریف actions به عنوان property
    actions = [mark_resolved]

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'updated_at']
    readonly_fields = ['updated_at']
    list_per_page = 20
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False  # جلوگیری از حذف تنظیمات سیستم