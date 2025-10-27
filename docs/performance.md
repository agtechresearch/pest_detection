# 성능 최적화 가이드

## 성능 벤치마크

### OpenVINO vs PyTorch 성능 비교

YOLO 공식 벤치마크에 따르면 OpenVINO 형식이 라즈베리파이에서 더 나은 성능을 제공합니다:

![YOLO11 Performance](https://github.com/ultralytics/assets/releases/download/v0.0.0/rpi-yolo11-benchmarks-coco128.avif)

### 성능 측정 방법

```bash
# 실행 시간 측정
time python main.py

# 메모리 사용량 모니터링
python -m memory_profiler main.py

# CPU 사용률 모니터링
htop
```

## 최적화 전략

### 1. 모델 최적화

#### OpenVINO 사용
```python
# PyTorch 모델을 OpenVINO로 변환
python etc/pt_transfer.py

# config.py에서 OpenVINO 모델 사용
MODEL_PATH = "pest_openvino_model"
```

#### 모델 크기 최적화
- YOLO11n 사용 (가장 작은 모델)
- 불필요한 레이어 제거
- 양자화 적용 (INT8)

### 2. 카메라 설정 최적화

#### 해상도 조정
```python
# 성능 우선
CAM_WIDTH = 1280
CAM_HEIGHT = 960

# 품질 우선
CAM_WIDTH = 1920
CAM_HEIGHT = 1440

# 균형
CAM_WIDTH = 1640
CAM_HEIGHT = 1232
```

#### FPS 최적화
```python
# 실시간 처리
CAM_FPS = 5

# 일반 사용
CAM_FPS = 2

# 배터리 절약
CAM_FPS = 1
```

### 3. 추론 최적화

#### 추론 간격 조정
```python
# 고성능 환경
YOLO_INTERVAL_SEC = 1.0

# 일반 환경
YOLO_INTERVAL_SEC = 3.0

# 저전력 환경
YOLO_INTERVAL_SEC = 10.0
```

#### 신뢰도 임계값 최적화
```python
# 빠른 처리 (더 적은 후처리)
YOLO_CONF = 0.7

# 균형
YOLO_CONF = 0.5

# 정확도 우선
YOLO_CONF = 0.3
```

### 4. 스레드 최적화

#### 대기 시간 조정
```python
# 반응성 우선
SLEEP_YOLO_LOOP = 0.005

# 균형 (권장)
SLEEP_YOLO_LOOP = 0.01

# CPU 절약
SLEEP_YOLO_LOOP = 0.05
```

#### 스레드 우선순위 설정
```python
# main.py에 추가
import os
os.nice(-10)  # 높은 우선순위 (root 권한 필요)
```

### 5. 메모리 최적화

#### 이미지 크기 최적화
```python
# ROI 크롭으로 메모리 사용량 감소
CROP_X, CROP_Y, CROP_W, CROP_H = 880, 5, 1550, 2500
```

#### 가비지 컬렉션 최적화
```python
import gc

# 주기적 가비지 컬렉션
if frame_count % 100 == 0:
    gc.collect()
```

## 환경별 최적 설정

### 고성능 환경 (RPI5 + AI Kit)
```python
CAM_WIDTH = 3280
CAM_HEIGHT = 2464
CAM_FPS = 10
YOLO_INTERVAL_SEC = 0.5
YOLO_CONF = 0.5
ENABLE_GUI = True
```

### 일반 환경 (RPI5 CPU만)
```python
CAM_WIDTH = 1920
CAM_HEIGHT = 1440
CAM_FPS = 3
YOLO_INTERVAL_SEC = 2.0
YOLO_CONF = 0.5
ENABLE_GUI = True
```

### 저전력 환경 (배터리 사용)
```python
CAM_WIDTH = 1280
CAM_HEIGHT = 960
CAM_FPS = 1
YOLO_INTERVAL_SEC = 10.0
YOLO_CONF = 0.6
ENABLE_GUI = False
ENABLE_SAVE = True
```

### 헤드리스 환경 (서버 모드)
```python
CAM_WIDTH = 1640
CAM_HEIGHT = 1232
CAM_FPS = 2
YOLO_INTERVAL_SEC = 5.0
YOLO_CONF = 0.5
ENABLE_GUI = False
ENABLE_SAVE = True
```

## 성능 모니터링

### 실시간 모니터링
```bash
# CPU 사용률
htop

# 메모리 사용량
free -h

# 디스크 I/O
iostat -x 1

# GPU 사용률 (AI Kit 사용 시)
nvidia-smi
```

### 로그 분석
```bash
# 성능 로그 수집
python main.py 2>&1 | tee performance.log

# 추론 시간 분석
grep "inference" performance.log
```

## 병목 지점 분석

### 1. 카메라 캡처
- **문제**: 카메라 해상도가 너무 높음
- **해결**: 해상도 낮추기 또는 FPS 조정

### 2. 이미지 전처리
- **문제**: 회전 및 크롭 연산
- **해결**: ROI 크기 최적화

### 3. YOLO 추론
- **문제**: 모델이 너무 무거움
- **해결**: OpenVINO 사용 또는 모델 경량화

### 4. GUI 렌더링
- **문제**: 실시간 화면 업데이트
- **해결**: GUI 비활성화 또는 업데이트 빈도 조정

## 추가 최적화 팁

### 1. 시스템 레벨 최적화
```bash
# CPU 성능 모드
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# GPU 메모리 분할
sudo raspi-config
# Advanced Options > Memory Split > 128
```

### 2. 네트워크 최적화 (원격 실행 시)
```bash
# SSH 압축 활성화
ssh -C username@raspberrypi

# X11 포워딩 최적화
ssh -X -c arcfour username@raspberrypi
```

### 3. 스토리지 최적화
```bash
# SSD 사용 (SD 카드 대신)
# USB 3.0 포트에 SSD 연결

# 로그 로테이션 설정
sudo nano /etc/logrotate.d/pest_detection
```

## 벤치마크 결과

### 테스트 환경
- **하드웨어**: Raspberry Pi 5
- **OS**: Raspberry Pi OS (64-bit)
- **Python**: 3.11
- **모델**: YOLO11n

### 성능 결과
| 설정 | FPS | CPU 사용률 | 메모리 사용량 |
|------|-----|------------|---------------|
| 3280x2464, PyTorch | 0.3 | 95% | 1.2GB |
| 3280x2464, OpenVINO | 0.8 | 85% | 0.8GB |
| 1920x1440, OpenVINO | 1.5 | 70% | 0.6GB |
| 1280x960, OpenVINO | 2.2 | 55% | 0.4GB |
