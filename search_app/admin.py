from django.contrib import admin
from .models import ImageRecord

@admin.register(ImageRecord)
class ImageRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "image_url", "result_class", "retry_count", "processed", "created_at", "failed_at")
    list_filter = ("processed", "retry_count", "created_at")
    search_fields = ("image_url", "result_class", "error_message")
