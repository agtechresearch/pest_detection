# 설치 및 설정 가이드

## 환경 요구사항

### 하드웨어
- 라즈베리파이 5 (Raspberry Pi 5)
- Pi Camera Module V2 (8MP)
- 3D 프린터로 제작된 커스텀 프레임

### 소프트웨어
- Raspberry Pi OS (최신 버전 권장)
- Python 3.8 이상
- 가상환경 (권장)

## 설치 과정

### 1. 시스템 준비
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필요한 패키지 설치
sudo apt install -y python3-pip python3-venv git
```

### 2. 카메라 설정
```bash
# 카메라 활성화
sudo raspi-config
# Interface Options > Camera > Enable 선택

# 재부팅
sudo reboot
```

### 3. 프로젝트 클론 및 환경 설정
```bash
# 프로젝트 클론
git clone [repository-url]
cd pest_detection

# 가상환경 생성 및 활성화
python3 -m venv yolo_env
source yolo_env/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. 모델 준비
```bash
# PyTorch 모델을 OpenVINO로 변환
python etc/pt_transfer.py
```

### 5. 실행 테스트
```bash
python main.py
```

## 초기 설정 확인

### 카메라 테스트
```bash
# 카메라 연결 확인
libcamera-hello --list-cameras
```

### 모델 테스트
```bash
# YOLO 모델 테스트
python etc/yolo_test.py
```

## 다음 단계
- [설정 옵션 가이드](configuration.md) 참고
- [성능 최적화](performance.md) 확인
- 문제 발생 시 [문제 해결 가이드](troubleshooting.md) 참고
