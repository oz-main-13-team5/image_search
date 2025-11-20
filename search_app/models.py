from django.db import models
from django.utils import timezone

class ImageRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    image_url = models.CharField(max_length=1000)
    result_class = models.CharField(max_length=255, null=True, blank=True)
    result_json = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    def mark_processed(self, result_class: str, result_json: dict) -> None:
        self.result_class = result_class
        self.result_json = result_json
        self.status = self.Status.PROCESSED
        self.processed_at = timezone.now()

    def mark_failed(self, error_message: str) -> None:
        self.error_message = error_message
        self.status = self.Status.FAILED
        self.failed_at = timezone.now()

    def __str__(self):
        return f"{self.image_url} -> {self.status}"

