import time
from django.conf import settings
from ultralytics import YOLO
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

# Session 재사용
_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0"})

# 모델 초기화 (settings에서 경로 읽기)
MODEL_PATH = settings.YOLO_MODEL_PATH
model = YOLO(MODEL_PATH).to("cpu")

# 0.25 이하는 불확실 정보 취급
CONF_THRESH = getattr(settings, "YOLO_CONF_THRESH", 0.25)

# 이미지 타입 검증
def _is_image_content_type(ct: str) -> bool:
    if not ct:
        return False
    ct = ct.lower()
    return "image" in ct or ct.endswith("octet-stream")

def analyze_image(url: str):
    # 네트워크 요청 안정화
    resp = _session.get(url, timeout=10)
    resp.raise_for_status()

    # 이미지 응답인지 확인
    ct = resp.headers.get("Content-Type", "")
    if not _is_image_content_type(ct):
        raise ValueError(f"Not an image response: Content-Type={ct}")

    try:
        img = Image.open(BytesIO(resp.content)).convert("RGB")
    except UnidentifiedImageError as e:
        raise ValueError(f"cannot identify image file: {e}")

    # 추론 타이밍
    start = time.time()
    results = model(img, device="cpu")
    elapsed_ms = (time.time() - start) * 1000.0

    detections = []
    if len(results[0].boxes) > 0:
        for box in results[0].boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())
            # 안전하게 names 매핑
            names_map = results[0].names
            label = names_map.get(cls_id, f"class_{cls_id}")
            detections.append({"label": label, "confidence": conf})

    # meta = 추론시간 + 모델 경로 + 타임 스탬프
    meta = {
        "inference_ms": elapsed_ms,
        "model_path": MODEL_PATH,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }

    result_json = {"detections": detections, "meta": meta}

    # 대표 라벨 결정
    if not detections:
        return "없음", result_json

    top = max(detections, key=lambda x: x["confidence"])
    top_label = top["label"] if top["confidence"] >= CONF_THRESH else "없음"
    return top_label, result_json
