import os
import requests
from io import BytesIO
from PIL import Image
from ultralytics import YOLO

# YOLO 모델 경로 설정
MODEL_PATH = os.path.join("image_search_server", "model_files", "best.pt")
model = YOLO(MODEL_PATH)

def analyze_image(url: str):
    try:
        print(f"🔍 이미지 다운로드 중: {url}")
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))

        print("🤖 YOLO 분석 시작...")
        results = model(image)

        labels = [results[0].names[int(c)] for c in results[0].boxes.cls]

        if labels:
            print("✅ 분석 결과:", ", ".join(labels))
        else:
            print("⚠️ 객체를 찾지 못했습니다")

    except Exception as e:
        print("❌ 오류:", e)


if __name__ == "__main__":
    test_url = input("테스트할 이미지 URL을 입력하세요:\n> ")
    analyze_image(test_url)
