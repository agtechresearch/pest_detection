# 문제 해결 가이드

## 일반적인 문제들

### 1. 카메라 관련 문제

#### 카메라가 인식되지 않음
**증상**: `Camera capture error` 또는 카메라 초기화 실패

**해결 방법**:
```bash
# 카메라 연결 확인
ls /dev/video*

# 카메라 활성화
sudo raspi-config
# Interface Options > Camera > Enable

# 재부팅
sudo reboot

# 카메라 테스트
libcamera-hello --list-cameras
```

#### 카메라 권한 오류
**증상**: `Permission denied` 오류

**해결 방법**:
```bash
# 사용자를 video 그룹에 추가
sudo usermod -a -G video $USER

# 재로그인 또는 재부팅
```

#### 카메라 해상도 오류
**증상**: `Requested resolution not supported` 오류

**해결 방법**:
```python
# config.py에서 지원되는 해상도로 변경
CAM_WIDTH = 1920   # 3280 대신
CAM_HEIGHT = 1440  # 2464 대신
```

### 2. 모델 관련 문제

#### 모델 로딩 실패
**증상**: `Model loading failed` 또는 `File not found` 오류

**해결 방법**:
```bash
# 모델 폴더 확인
ls -la pest_openvino_model/

# 모델 변환 실행
python etc/pt_transfer.py

# 모델 테스트
python etc/yolo_test.py
```

#### OpenVINO 모델 오류
**증상**: `OpenVINO inference failed` 오류

**해결 방법**:
```bash
# OpenVINO 재설치
pip uninstall openvino
pip install openvino

# 모델 재변환
rm -rf pest_openvino_model/
python etc/pt_transfer.py
```

### 3. 성능 관련 문제

#### CPU 사용률 100%
**증상**: 시스템이 느려지거나 프레임 드롭 발생

**해결 방법**:
```python
# config.py 수정
CAM_FPS = 1                    # FPS 낮추기
YOLO_INTERVAL_SEC = 5.0        # 추론 간격 늘리기
ENABLE_GUI = False             # GUI 비활성화
```

#### 메모리 부족
**증상**: `Out of memory` 오류

**해결 방법**:
```python
# 해상도 낮추기
CAM_WIDTH = 1280
CAM_HEIGHT = 960

# 스왑 메모리 활성화
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048로 변경
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 4. GUI 관련 문제

#### GUI 창이 나타나지 않음
**증상**: 프로그램은 실행되지만 화면에 아무것도 표시되지 않음

**해결 방법**:
```python
# config.py 확인
ENABLE_GUI = True

# 디스플레이 확인
echo $DISPLAY

# SSH 연결인 경우 X11 포워딩 활성화
ssh -X username@raspberrypi
```

#### GUI 창 크기 문제
**증상**: GUI 창이 화면을 벗어나거나 너무 작음

**해결 방법**:
```python
# 자동 크기 조정이 활성화되어 있는지 확인
# main.py의 detect_screen_size() 함수가 정상 작동하는지 확인
```

### 5. 저장 관련 문제

#### 이미지 저장 실패
**증상**: `File save error` 또는 저장 폴더 접근 오류

**해결 방법**:
```bash
# 저장 폴더 생성
mkdir -p captures/origin
mkdir -p captures/detected

# 권한 설정
chmod 755 captures/
chmod 755 captures/origin/
chmod 755 captures/detected/
```

#### 디스크 공간 부족
**증상**: `No space left on device` 오류

**해결 방법**:
```bash
# 디스크 사용량 확인
df -h

# 불필요한 파일 삭제
sudo apt autoremove
sudo apt autoclean

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

## 로그 분석

### 일반적인 로그 메시지

#### 정상 작동
```
Camera capture thread started.
YOLO inference thread started.
Main thread started (GUI & Save handler).
```

#### 오류 메시지
```
Capture error: [오류 내용]
Model loading failed: [오류 내용]
File save error: [오류 내용]
```

### 디버깅 모드 활성화

```python
# config.py에 추가
DEBUG_MODE = True

# 또는 실행 시 디버그 정보 출력
python main.py --debug
```

## 성능 모니터링

### 시스템 리소스 확인
```bash
# CPU 사용률
htop

# 메모리 사용량
free -h

# 디스크 I/O
iostat -x 1

# 네트워크 사용량
iftop
```

### 프로세스 모니터링
```bash
# Python 프로세스 확인
ps aux | grep python

# 스레드 확인
top -H -p [PID]
```

## 추가 도움

문제가 지속되면 다음 정보와 함께 이슈를 등록하세요:

1. 라즈베리파이 모델 및 OS 버전
2. Python 버전
3. 설치된 패키지 목록 (`pip list`)
4. 오류 로그 전체 내용
5. `config.py` 설정값
