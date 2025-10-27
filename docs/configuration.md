# 설정 옵션 가이드

`config.py` 파일에서 시스템의 모든 설정을 조정할 수 있습니다.

## 카메라 설정

### 기본 카메라 설정
```python
CAM_WIDTH = 3280      # 카메라 해상도 (가로)
CAM_HEIGHT = 2464     # 카메라 해상도 (세로)
CAM_FPS = 1           # 프레임 레이트
```

### 해상도 선택 가이드
- **고해상도 (3280x2464)**: 최고 품질, 높은 CPU 사용량
- **중해상도 (1920x1440)**: 균형잡힌 성능
- **저해상도 (1280x960)**: 최고 성능, 낮은 품질

### FPS 설정
- **1 FPS**: 정적 모니터링에 적합
- **5-10 FPS**: 실시간 모니터링
- **15+ FPS**: 고속 움직임 감지

## 모델 설정

### 기본 모델 설정
```python
MODEL_PATH = "pest_openvino_model"  # 모델 경로
YOLO_CONF = 0.5                     # 탐지 신뢰도 임계값
YOLO_INTERVAL_SEC = 3.0             # 추론 간격 (초)
```

### 신뢰도 임계값 조정
- **0.3-0.4**: 더 많은 탐지 (False Positive 증가)
- **0.5-0.6**: 균형잡힌 탐지 (권장)
- **0.7-0.8**: 높은 정확도 (False Negative 증가)

### 추론 간격 조정
- **1-2초**: 실시간 모니터링
- **3-5초**: 일반적인 사용 (권장)
- **10초+**: 배터리 절약 모드

## 기능 활성화

### GUI 및 저장 설정
```python
ENABLE_GUI = True      # 실시간 GUI 표시
ENABLE_SAVE = False    # 주기적 이미지 저장
```

### GUI 설정
- **True**: 실시간 탐지 결과 시각화
- **False**: 백그라운드 실행 (성능 향상)

### 저장 설정
```python
SAVE_INTERVAL = 10     # 이미지 저장 간격 (초)
SAVE_PATH_ORIGINAL = "captures/origin"     # 원본 이미지 저장 경로
SAVE_PATH_DETECTED = "captures/detected"   # 탐지 결과 저장 경로
```

## 성능 관련 설정

### 스레드 대기 시간
```python
SLEEP_YOLO_LOOP = 0.01      # YOLO 스레드 대기 시간
SLEEP_CAPTURE_ERROR = 0.1   # 카메라 오류 시 대기 시간
SLEEP_MAIN_NO_GUI = 0.1     # GUI 비활성화 시 메인 스레드 대기 시간
```

### 권장 설정값
- **SLEEP_YOLO_LOOP**: 0.01초 (10ms) - CPU 사용량과 반응성의 균형
- **SLEEP_CAPTURE_ERROR**: 0.1초 - 오류 로그 스팸 방지
- **SLEEP_MAIN_NO_GUI**: 0.1초 - GUI 없을 때 CPU 절약

## 시각화 설정

### GUI 창 설정
```python
GUI_WINDOW_NAME = "Pest Detection Live Feed"
```

### BBox 설정 (주석 해제하여 사용)
```python
# BBOX_COLOR = (0, 0, 255)    # BGR 색상 (빨간색)
# BBOX_THICKNESS = 2          # 박스 두께
```

## 환경별 권장 설정

### 고성능 환경 (RPI5 + AI Kit)
```python
CAM_WIDTH = 3280
CAM_HEIGHT = 2464
CAM_FPS = 5
YOLO_INTERVAL_SEC = 1.0
ENABLE_GUI = True
```

### 일반 환경 (RPI5 CPU만)
```python
CAM_WIDTH = 1920
CAM_HEIGHT = 1440
CAM_FPS = 2
YOLO_INTERVAL_SEC = 3.0
ENABLE_GUI = True
```

### 저전력 환경 (배터리 사용)
```python
CAM_WIDTH = 1280
CAM_HEIGHT = 960
CAM_FPS = 1
YOLO_INTERVAL_SEC = 10.0
ENABLE_GUI = False
ENABLE_SAVE = True
```
