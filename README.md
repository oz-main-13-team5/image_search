1. 개요
이 서비스는 DB에 저장된 이미지 URL을 주기적으로 확인하고, YOLO 모델을 사용해 분석한 결과를 다시 DB에 기록합니다.
Django 커스텀 커맨드(run_scheduler)와 systemd를 이용해 서버에서 자동으로 실행되도록 구성했습니다.

2. 주요 구성 요소
(1) Model: ImageRecord
DB 테이블은 이미지 분석 작업을 관리합니다.

필드명	타입	설명
image_url	CharField(1000)	분석할 이미지 URL
result_class	CharField(255)	대표 라벨 (confidence 가장 높은 클래스)
result_json	JSONField	전체 추론 결과 (라벨+confidence+메타정보)
error_message	TextField	실패 시 에러 메시지
retry_count	IntegerField	실패 횟수 (최대 3회)
created_at	DateTimeField	레코드 생성 시각
processed	BooleanField	처리 완료 여부
failed_at	DateTimeField	실패 확정 시각

(2) Task Scheduler: tasks.py
run_once()

DB에서 processed=False이고 retry_count<3인 레코드를 조회

YOLO 추론 실행 (analyze_image)

결과를 DB에 저장 (result_class, result_json, processed=True)

실패 시 retry_count 증가, 3회 이상이면 failed_at 기록

run_scheduler(interval_seconds=60)

기본 60초마다 run_once() 실행

SIGTERM/SIGINT 신호를 받아 안전하게 종료

(3) Django Command: run_scheduler.py
python manage.py run_scheduler --interval 60

내부적으로 tasks.run_scheduler() 호출

systemd 서비스에서 이 커맨드를 실행하도록 설정

3. systemd 설정 방법
서비스 유닛 파일 작성 /etc/systemd/system/yolo-scheduler.service

ini
[Unit]
Description=YOLO Image Analysis Scheduler
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/DjangoProject
ExecStart=/home/ubuntu/.venv/bin/python manage.py run_scheduler --interval 60
Restart=always
User=ubuntu
Environment="DJANGO_SETTINGS_MODULE=image_search_server.settings"

[Install]
WantedBy=multi-user.target
systemd 리로드 및 서비스 시작

bash
sudo systemctl daemon-reload
sudo systemctl enable yolo-scheduler
sudo systemctl start yolo-scheduler
상태 확인

bash
sudo systemctl status yolo-scheduler
로그 확인

bash
journalctl -u yolo-scheduler -f

4. 운영 시 주의사항
로그 확인: systemd 로그(journalctl)에서 에러 메시지를 확인 가능.

재시도 정책: 최대 3회까지 자동 재시도 후 실패 처리.

모델 교체: settings.YOLO_MODEL_PATH를 변경하면 다른 YOLO 모델로 교체 가능.