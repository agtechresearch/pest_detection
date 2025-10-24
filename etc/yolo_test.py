from ultralytics import YOLO

# Load the exported NCNN model
ncnn_model = YOLO("best_openvino_model")

# Run inference
results = ncnn_model("test.jpg")
print(results)