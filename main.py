from picamera2 import Picamera2
import numpy as np
import time
import threading
from threading import Lock
import cv2
import os
import tkinter as tk

from ultralytics import YOLO
import config


class RealtimeCamera:
    def __init__(self, width=config.CAM_WIDTH, height=config.CAM_HEIGHT, fps=config.CAM_FPS):
        """
        실시간 촬영 카메라 클래스
        """
        self.picam2 = Picamera2()
        self.latest_frame = None
        self.frame_lock = Lock()        
        self.is_running = False
        self.capture_thread = None

        print(f"Requested resolution: {width}x{height} @ {fps}fps")
        
        # 카메라 설정
        self.camera_config = self.picam2.create_still_configuration(
            main={"size": (width, height), "format": "RGB888"},
            controls={"FrameRate": fps}
        )
        self.picam2.align_configuration(self.camera_config)
        self.picam2.configure(self.camera_config)

        # 실제로 적용된 해상도 확인
        actual_config = self.picam2.camera_configuration()
        print(f"Actual resolution set: {actual_config['main']['size']} @ {actual_config['controls']['FrameRate']}fps (Format: {actual_config['main']['format']})")
    def start_capture(self):
        """카메라 시작 및 백그라운드 캡처 시작"""
        self.picam2.start()
        self.is_running = True
        
        # 백그라운드 캡처 스레드 시작
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Camera capture thread started.")

    def _capture_loop(self):
        """백그라운드에서 지속적으로 프레임 캡처"""
        while self.is_running:
            try:
                # 프레임 캡처
                frame = self.picam2.capture_array()
                
                # Lock을 잡고 최신 프레임 변수를 업데이트
                with self.frame_lock:
                    self.latest_frame = frame
            
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(config.SLEEP_CAPTURE_ERROR)
    
    def get_latest_frame(self):
        """가장 최근 프레임의 복사본을 반환"""
        frame_copy = None
        with self.frame_lock:
            if self.latest_frame is not None:
                frame_copy = self.latest_frame.copy()
        return frame_copy
    
    def save_frame(self, frame, filename):
        """특정 프레임을 파일로 저장"""
        if frame is None:
            print(f"Save failed: {filename} (frame is None)")
            return False
        
        try:
            # OpenCV로 이미지 저장
            cv2.imwrite(filename, frame)
            print(f"Image saved: {filename}")
            return True
        except Exception as e:
            print(f"File save error: {e} (Path: {filename})")
            return False
    
    def stop_capture(self):
        """캡처 중지"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join()
        self.picam2.stop()
        self.picam2.close()
        print("Camera capture stopped.")


print("Loading YOLO model...")
model = YOLO(config.MODEL_PATH)
print("YOLO model loaded.")

def yolo_inference_loop(camera_instance, data_lock, shared_data):
    """
    YOLO 추론을 실행하고, 결과를 shared_data에 저장
    - data_lock: shared_data 접근을 위한 Lock
    - shared_data: 감지 결과를 메인 스레드와 공유하기 위한 딕셔너리
    """
    print("YOLO inference thread started.")

    # 전처리 설정값 (ROI 영역)
    CROP_X, CROP_Y, CROP_W, CROP_H = 880, 5, 1550, 2500

    target_interval = config.YOLO_INTERVAL_SEC

    while camera_instance.is_running:
        loop_start_time = time.time()   # 추론 시간 조정을 위한 시작 시간
        
        frame = camera_instance.get_latest_frame()      # 가장 최신 프레임 가져오기
        if frame is None:
            # 아직 캡처 스레드가 첫 프레임을 만들지 못할 경우 대기
            time.sleep(config.SLEEP_YOLO_LOOP)
            continue

        # 전처리 로직 (회전 -> 크롭)
        frame_rotated = cv2.rotate(frame, cv2.ROTATE_180)
        frame_cropped = crop_roi(frame_rotated, CROP_X, CROP_Y, CROP_W, CROP_H)

        # YOLO 추론 실행
        results_list = model(frame_cropped, conf=config.YOLO_CONF, verbose=False)

        # 추론 결과(bbox)를 crop된 이미지에 그리기
        gui_frame = frame_cropped.copy()
        detected_objects = []

        if results_list and len(results_list[0].boxes) > 0:
            results = results_list[0]
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = f"{results.names[cls_id]} ({conf:.2f})"
                detected_objects.append({'label': label, 'conf': conf, 'bbox': [x1, y1, x2, y2]})

                # gui_frame에 bbox 그리기
                cv2.rectangle(gui_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(gui_frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        with data_lock:
            shared_data['original_frame'] = frame_rotated       # 원본 저장용 (회전만 된 고해상도 RGB)
            shared_data['gui_frame'] = gui_frame                # 탐지/GUI용 (crop + bboxes)
            shared_data['detections'] = detected_objects        # (option) bbox 리스트
        
        # 추론 간격 조정
        loop_end_time = time.time()
        elapsed_time = loop_end_time - loop_start_time
        sleep_time = target_interval - elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("YOLO inference thread stopped.")

def crop_roi(frame, x, y, width, height):
    """프레임에서 ROI 영역을 자르는 함수"""
    h, w = frame.shape[:2]
    
    # 경계 확인 및 조정
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    x2 = min(x + width, w)
    y2 = min(y + height, h)
    
    return frame[y:y2, x:x2]

def detect_screen_size(width=1920, height=1080):
    # 모니터 해상도 자동 감지
    screen_width = width
    screen_height = height
    try:
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
    except Exception as e:
        print(f"Could not get screen resolution (error: {e}). Using default 1920x1080.")
    
    # 화면에 표시할 최대 크기 (비율 유지를 위함)
    MAX_DISPLAY_WIDTH = int(screen_width * 0.85)
    MAX_DISPLAY_HEIGHT = int(screen_height * 0.85)
    return MAX_DISPLAY_WIDTH, MAX_DISPLAY_HEIGHT



# 메인 실행부
if __name__ == "__main__":
    # 저장 폴더 생성 (원본/탐지 폴더 두 곳 생성)
    if config.ENABLE_SAVE:
        os.makedirs(config.SAVE_PATH_ORIGINAL, exist_ok=True)
        os.makedirs(config.SAVE_PATH_DETECTED, exist_ok=True)
        print(f"Original save path: {config.SAVE_PATH_ORIGINAL}")
        print(f"Detected save path: {config.SAVE_PATH_DETECTED}")
    
    # 스레드 간 감지 결과 공유용 변수
    shared_data = {'original_frame': None, 'gui_frame': None, 'detections': []}
    data_lock = threading.Lock()

    # 카메라 및 스레드 초기화
    camera = RealtimeCamera(width=config.CAM_WIDTH, height=config.CAM_HEIGHT, fps=config.CAM_FPS)
    yolo_thread = None
    last_save_time = time.time()
    last_gui_time = time.time()
    
    # 화면 해상도 자동 감지
    MAX_DISPLAY_WIDTH, MAX_DISPLAY_HEIGHT = detect_screen_size()
    print(f"Detected screen resolution: {MAX_DISPLAY_WIDTH}x{MAX_DISPLAY_HEIGHT}")

    try:
        # 실시간 캡처 스레드 시작 (생산자)
        camera.start_capture()

        # YOLO 추론 스레드 시작 (소비자)
        yolo_thread = threading.Thread(
            target=yolo_inference_loop,
            args=(camera, data_lock, shared_data),
            daemon=True
        )
        yolo_thread.start()

        print("Main thread started (GUI & Save handler). Press 'q' to quit.")

        while True:
            # 최신 프레임 가져오기
            current_original_frame = None
            current_gui_frame = None

            with data_lock:
                if shared_data['original_frame'] is not None:
                    current_original_frame = shared_data['original_frame'].copy()
                if shared_data['gui_frame'] is not None:
                    current_gui_frame = shared_data['gui_frame'].copy()

            if current_gui_frame is None or current_original_frame is None:
                time.sleep(config.SLEEP_YOLO_LOOP)
                continue

            # 주기적 저장
            current_time = time.time()
            if config.ENABLE_SAVE and current_time - last_save_time >= config.SAVE_INTERVAL:
                timestamp = int(current_time)

                # 원본 저장
                filename_origin = os.path.join(
                    config.SAVE_PATH_ORIGINAL,
                    f"capture_org_{timestamp}.jpg"
                )
                camera.save_frame(current_original_frame, filename=filename_origin)

                # 탐지 결과 저장
                filename_det = os.path.join(
                    config.SAVE_PATH_DETECTED,
                    f"capture_det_{timestamp}.jpg"
                )
                camera.save_frame(current_gui_frame, filename=filename_det)

                last_save_time = current_time

            # GUI 시각화            
            if not config.ENABLE_GUI:
                if not yolo_thread.is_alive() or not camera.capture_thread.is_alive():
                    print("Background thread stopped. Exiting main loop.")
                    break
                time.sleep(config.SLEEP_MAIN_NO_GUI)
            if config.ENABLE_GUI:
                # # 3초마다 realtime_*.jpg 파일 저장
                # if current_time - last_gui_time >= 3.0:
                #     realtime_origin_path = os.path.join(
                #         config.BASE_PATH,
                #         f"realtime_origin.jpg"
                #     )
                #     realtime_gui_path = os.path.join(
                #         config.BASE_PATH,
                #         f"realtime_detected.jpg"
                #     )
                #     camera.save_frame(current_original_frame, filename=realtime_origin_path)
                #     camera.save_frame(current_gui_frame, filename=realtime_gui_path)
                #     last_gui_time = current_time

                # 화면 크기에 맞춰 자동 resize (원본 비율을 유지하면서 모니터 크기에 맞춤)
                img_h, img_w = current_gui_frame.shape[:2]
                ratio = min(MAX_DISPLAY_WIDTH / img_w, MAX_DISPLAY_HEIGHT / img_h)
                new_w = int(img_w * ratio)
                new_h = int(img_h * ratio)

                # 리사이즈
                display_frame = cv2.resize(current_gui_frame, (new_w, new_h),
                                           interpolation=cv2.INTER_AREA)

                cv2.imshow(config.GUI_WINDOW_NAME, display_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Shutting down.")

    finally:
        # 정리
        print("Starting cleanup...")

        camera.is_running = False
        camera.stop_capture()

        if yolo_thread:
            yolo_thread.join(timeout=3.0)

        if config.ENABLE_GUI:
            cv2.destroyAllWindows()

        print("Cleanup complete.")

    print("Program finished.")
