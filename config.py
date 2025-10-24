import os

# 기본 경로 설정 (가장 중요)
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
# 원본 이미지를 저장할 폴더 경로 (BASE_PATH 기준)
SAVE_PATH_ORIGINAL = os.path.join(BASE_PATH, "captures", "origin")
# 탐지 결과(BBox)가 그려진 이미지를 저장할 폴더 경로
SAVE_PATH_DETECTED = os.path.join(BASE_PATH, "captures", "detected")

# 카메라 및 모델 설정
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 10

MODEL_PATH = "best_openvino_model"

# 기능 활성화 스위치
ENABLE_GUI = False       # True: 실시간 GUI (cv2.imshow) 창을 출력
ENABLE_SAVE = True      # True: 주기적 이미지 저장을 활성화

# 저장 설정
SAVE_INTERVAL = 10      # 이미지를 저장할 간격 (초)

# 스레드 및 GUI 설정 (성능 관련)
# [필수] YOLO 스레드가 프레임이 없을 때 대기하는 시간 (초)
# 0.01 (10ms) 정도가 CPU 낭비(Busy-waiting)를 막으면서 반응성을 유지하기에 적절
SLEEP_YOLO_LOOP = 0.01

# [필수] 카메라 하드웨어 오류 발생 시 대기 시간 (초)
# 0.1 ~ 1.0초가 적절. 오류 로그가 콘솔을 도배하는 것을 방지
SLEEP_CAPTURE_ERROR = 0.1

# [필수] GUI 비활성화 시 메인 스레드 대기 시간 (초)
# 0.1 (100ms) 정도가 적절. GUI가 꺼졌을 때 메인 스레드가 
# CPU 100%를 사용하는 것을 방지 (cv2.waitKey(1)의 대체)
SLEEP_MAIN_NO_GUI = 0.1

# 시각화(BBox) 설정
GUI_WINDOW_NAME = "YOLO Live Feed (RPi4)"
BBOX_COLOR = (255, 0, 0)
BBOX_THICKNESS = 2