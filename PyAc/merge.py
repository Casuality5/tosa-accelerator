import cv2
import numpy as np
from ultralytics import YOLO
from sentence_transformers import SentenceTransformer, util

class VegaProcessor:
    def __init__(self):
        print("Loading YOLOv8n model...")
        self.detection_model = YOLO('yolov8n.pt') 
        
        print("Loading MiniLM model for task and label encoding...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get YOLO class names (person, car, fire extinguisher, etc.)
        self.class_names = self.detection_model.names

    def resize_and_normalize(self, image_path, target_size=(640, 640)):
        img = cv2.imread(image_path)
        if img is None: return None
        resized_img = cv2.resize(img, target_size)
        return resized_img / 255.0

    def detect_and_crop(self, image_path, normalized_img):
        results = self.detection_model(image_path)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        class_ids = results[0].boxes.cls.cpu().numpy()
        
        patches = []
        for i in range(len(boxes)):
            x_min, y_min, x_max, y_max = map(int, boxes[i])
            patch = normalized_img[y_min:y_max, x_min:x_max]
            
            patches.append({
                "class_id": int(class_ids[i]),
                "class_name": self.class_names[int(class_ids[i])],
                "patch": patch
            })
        return patches

    def generate_weights(self, task_embedding, object_patches):
        """
        Calculates similarity weights between the task and each object patch.
        """
        weights = []
        for obj in object_patches:
            # Encode the name of the detected object (e.g., "fire extinguisher")
            label_embedding = self.encoder.encode(obj["class_name"])
            
            # Calculate Cosine Similarity (Weight)
            similarity = util.cos_sim(task_embedding, label_embedding).item()
            weights.append(round(similarity, 4))
            
        return weights

    def get_complete_payload(self, image_path, task_query):
        """
        The main merge: Returns task_embedding, object_patches, AND weights.
        """
        # 1. Process Task
        task_embedding = self.encoder.encode(task_query)
        
        # 2. Process Vision
        norm_img = self.resize_and_normalize(image_path)
        object_patches = self.detect_and_crop(image_path, norm_img)
        
        # 3. Generate Weights
        relevance_weights = self.generate_weights(task_embedding, object_patches)
        
        return {
            "task_embedding": task_embedding,
            "object_patches": object_patches,
            "weights": relevance_weights
        }

# --- Usage ---
# vega = VegaProcessor()
# result = vega.get_complete_payload("office.jpg", "Find the fire extinguisher")
# print(f"Detected: {[p['class_name'] for p in result['object_patches']]}")
# print(f"Weights: {result['weights']}")