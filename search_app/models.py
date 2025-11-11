from django.db import models

class ImageRecord(models.Model):
    image_url = models.CharField(max_length=1000)  # URL 길이 넉넉히
    result_class = models.CharField(max_length=255, null=True, blank=True)  # 대표 라벨
    result_json = models.JSONField(null=True, blank=True)  # 전체 결과 저장
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)  # 실패 횟수 기록
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시각 기록
    processed = models.BooleanField(default=False) # 성공 시각 기록
    failed_at = models.DateTimeField(null=True, blank=True)  # 실패 시각 기록

    def __str__(self):
        status = self.result_class or self.error_message or "미처리"
        return f"{self.image_url} -> {status}"
