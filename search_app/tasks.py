import os
import time
import signal
import django
import logging
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "image_search_server.settings")
django.setup()

from search_app.models import ImageRecord
from search_app.yolo_inference import analyze_image

logger = logging.getLogger("search_app")

BATCH_SIZE = 100  # 한 번에 처리할 최대 레코드 수

_stop = False

def run_once():
    # 처리량 제한
    records = ImageRecord.objects.filter(processed=False, retry_count__lt=3).order_by("created_at")[:BATCH_SIZE]
    for record in records:
        # 각 코드 처리중 예외 관리
        try:
            result_class, result_json = analyze_image(record.image_url)
            record.result_class = result_class
            record.result_json = result_json
            record.processed = True
            record.save(update_fields=["result_class", "result_json", "processed"])
            logger.info(f"Processed {record.id} {record.image_url} -> {result_class}")
        except Exception as e:
            record.retry_count += 1
            record.error_message = str(e)
            if record.retry_count >= 3:
                record.processed = True
                record.failed_at = timezone.now()
            record.save(update_fields=["retry_count", "error_message", "processed", "failed_at"])
            logger.error(f"Failed {record.id} {record.image_url} (retry {record.retry_count}): {e}")


# sysytemd 정지 시작 코드
def _handle_stop(signum, frame):
    global _stop
    logger.info("Stop signal received, shutting down scheduler loop...")
    _stop = True

signal.signal(signal.SIGTERM, _handle_stop)
signal.signal(signal.SIGINT, _handle_stop)

def run_scheduler(interval_seconds: int = 60):
    logger.info("Starting run_scheduler")
    while not _stop:
        run_once()
        for _ in range(interval_seconds):
            if _stop:
                break
            time.sleep(1)
    logger.info("run_scheduler stopped")