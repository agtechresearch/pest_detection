from picamera2 import Picamera2
import numpy as np
import time
import threading
from threading import Lock
import cv2
import os

from ultralytics import YOLO
import config


class RealtimeCamera:
    def __init__(self, width=config.CAM_WIDTH, height=config.CAM_HEIGHT, fps=config.CAM_FPS):
        """
        실시간 카메라 클래스
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
            # OpenCV로 이미지 저장 (RGB -> BGR)
            #cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
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

    while camera_instance.is_running:
        # 가장 최신 프레임 가져오기
        frame = camera_instance.get_latest_frame()
        if frame is None:
            # 아직 캡처 스레드가 첫 프레임을 만들지 못함
            time.sleep(config.SLEEP_YOLO_LOOP)
            continue

        # YOLO 추론 실행
        results_list = model(frame, verbose=False)

        # 리스트가 비어있는지 확인하고, 첫 번째 결과를 꺼냅니다.
        if not results_list:
            #print("[Inference Thread] YOLO: 결과 리스트가 비어있습니다.")
            with data_lock:
                shared_data['detections'] = []
            continue
        
        results = results_list[0]
        detected_objects = []

        if len(results.boxes) > 0:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = results.names[cls_id]
                detected_objects.append({'label': label, 'conf': conf, 'bbox': [x1, y1, x2, y2]})
        
        with data_lock:
            shared_data['detections'] = detected_objects

    print("YOLO inference thread stopped.")


# 메인 실행부
if __name__ == "__main__":
    # 저장 폴더 생성 (원본/탐지 폴더 두 곳 생성)
    if config.ENABLE_SAVE:
        os.makedirs(config.SAVE_PATH_ORIGINAL, exist_ok=True)
        os.makedirs(config.SAVE_PATH_DETECTED, exist_ok=True)
        print(f"Original save path: {config.SAVE_PATH_ORIGINAL}")
        print(f"Detected save path: {config.SAVE_PATH_DETECTED}")
    
    # 스레드 간 감지 결과 공유용 변수
    shared_data = {'detections': []}
    data_lock = threading.Lock()

    # 카메라 및 스레드 초기화
    camera = RealtimeCamera(width=config.CAM_WIDTH, height=config.CAM_HEIGHT, fps=config.CAM_FPS)
    yolo_thread = None
    last_save_time = time.time()
    
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
            frame = camera.get_latest_frame()
            if frame is None:
                time.sleep(config.SLEEP_YOLO_LOOP)
                continue

            # 최신 감지 결과 가져오기
            current_detections = []
            with data_lock:
                # 얕은 복사(shallow copy)로 감지 목록을 가져옴
                current_detections = list(shared_data['detections'])
            
            # 원본 프레임 (저장용)
            display_frame = frame

            # Bbox 그릴 사본 프레임 (GUI 및 저장용)
            gui_frame = frame.copy()

            if current_detections:
                for det in current_detections:
                    x1, y1, x2, y2 = det['bbox']
                    label = f"{det['label']} (conf: {det['conf']:.2f})"
                    cv2.rectangle(gui_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(gui_frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # GUI 시각화
            if config.ENABLE_GUI:
                #bgr_frame = cv2.cvtColor(gui_frame, cv2.COLOR_RGB2BGR)
                bgr_frame = gui_frame
                cv2.imshow(config.GUI_WINDOW_NAME, bgr_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("'q' key pressed. Initiating shutdown...")
                    break
            
            # 주기적 저장
            current_time = time.time()
            if config.ENABLE_SAVE and current_time - last_save_time >= config.SAVE_INTERVAL:
                timestamp = int(current_time)

                # 원본 저장
                filename_origin = os.path.join(
                    config.SAVE_PATH_ORIGINAL,
                    f"capture_org_{timestamp}.jpg"
                )
                camera.save_frame(display_frame, filename=filename_origin)

                # 탐지 결과 저장
                filename_det = os.path.join(
                    config.SAVE_PATH_DETECTED,
                    f"capture_det_{timestamp}.jpg"
                )
                camera.save_frame(gui_frame, filename=filename_det)

                last_save_time = current_time
            
            if not config.ENABLE_GUI:
                if not yolo_thread.is_alive() or not camera.capture_thread.is_alive():
                    print("Background thread stopped. Exiting main loop.")
                    break
                time.sleep(config.SLEEP_MAIN_NO_GUI)
    
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
