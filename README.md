# 🐛 해충 트랩 탐지 시스템 (Pest Detection System)

라즈베리파이(RPI) 기반 실시간 해충 탐지 및 모니터링 시스템입니다. YOLO11n 모델을 OpenVINO로 최적화하여 라즈베리파이에서 효율적으로 동작할 수 있도록 구성하였습니다.

## 프로젝트 개요

본 repository는 병해충 과제에서 사용할 해충 트랩 탐지 모델의 실시간 운용을 목적으로 합니다. 라즈베리파이에서 카메라를 통해 실시간으로 이미지를 촬영하고, YOLO 모델을 사용하여 해충을 탐지하는 시스템입니다.

### 주요 특징

- **실시간 처리**: 멀티스레딩을 통한 카메라 캡처와 YOLO 추론의 병렬 처리
- **OpenVINO 최적화**: 라즈베리파이 성능에 맞춘 모델 최적화
- **유연한 설정**: `config.py`를 통한 쉬운 설정 변경
- **GUI 지원**: 실시간 탐지 결과 시각화 (Option)
- **자동 저장**: 주기적 이미지 저장 기능 (Option)

## 하드웨어 사양

- **메인 컴퓨터**: 라즈베리파이 5 (Raspberry Pi 5)
- **카메라**: Pi Camera Module V2 (8MP)
- **프레임**: 3D 프린터로 제작된 커스텀 프레임 (made by 은규)
- **추론**: CPU 기반 (AI Kit/AI Camera와 같은 NPU 미사용)

## 프로젝트 구조

```
pest_detection/
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 파일
├── pest_openvino_model/   # OpenVINO 최적화 모델 (Git 제외)
├── dataset_640.zip        # 데이터셋 (NAS에 업로드)
├── docs/                  # 상세 문서 정리 폴더
├── etc/                   # 유틸리티 및 테스트 파일
│   ├── pt_transfer.py     # PyTorch → OpenVINO 변환 스크립트
│   └── yolo_test.py       # YOLO 모델 테스트 스크립트
├── README.md
└── .gitignore
```

## 🚀 빠른 시작

### 1. 환경 설정
가상환경 이름과 디렉토리 경로는 컴퓨터 환경에 따라 다를 수 있습니다.

```bash
# 가상환경 활성화
source ~/yolo_env/bin/activate

# 프로젝트 디렉토리로 이동
cd Desktop/pest_detection
```

### 2. 실행

```bash
python main.py
```

### 3. 종료

- GUI 모드: `q` 키를 눌러 종료
- GUI 비활성화 모드: `Ctrl+C`로 종료

## ⚙️ 기본 설정

`config.py` 파일에서 주요 설정을 조정할 수 있습니다:

```python
# 카메라 설정
CAM_WIDTH = 3280
CAM_HEIGHT = 2464
CAM_FPS = 1

# 모델 설정
MODEL_PATH = "pest_openvino_model"
YOLO_CONF = 0.5
YOLO_INTERVAL_SEC = 3.0

# 기능 활성화
ENABLE_GUI = True
ENABLE_SAVE = False
```

## 📚 상세 문서

보다 상세한 문서는 `/docs` 폴더의 파일들을 참고해주세요.<br>
[Note!] 아래 문서들은 기본적인 틀만 작성되어 있고, 빠른 시일 내 업데이트 예정입니다!
- **[설치 및 설정 가이드](docs/setup.md)** - 상세한 설치 과정
- **[설정 옵션 가이드](docs/configuration.md)** - 모든 설정 옵션 설명
- **[성능 최적화](docs/performance.md)** - 성능 튜닝 및 벤치마크
- **[문제 해결 가이드](docs/troubleshooting.md)** - 일반적인 문제 해결

## 추가 코멘트

본 프로젝트는 해충 탐지 목적으로 개발되었지만, 라즈베리파이 기반의 실시간 객체 탐지 시스템으로 다양한 용도에 활용할 수 있습니다.

## 📄 라이선스

본 프로젝트는 연구 목적으로 개발되었습니다.