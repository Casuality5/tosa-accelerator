import cv2
import numpy as np
from ultralytics import YOLO

class VegaProcessor:
    def __init__(self):
        # Load the lightweight YOLOv8 Nano model for CPU inference
        print("Loading YOLOv8n model...")
        self.detection_model = YOLO('yolov8n.pt') 

    def resize_and_normalize(self, image_path, target_size=(640, 640)):
        """Reads, resizes, and normalizes a single image."""
        img = cv2.imread(image_path)

        if img is None:
            print(f"Error: Failed to load {image_path}")
            return None

        try:
            resized_img = cv2.resize(img, target_size)
            normalized_img = resized_img / 255.0
            return normalized_img

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

    def detect_objects(self, image_path):
        """
        Runs the Object Detection Module.
        Returns a list of Bounding Box Coordinates: [x_min, y_min, x_max, y_max]
        """
        # Run inference on the image. YOLO automatically handles its own 
        # internal resizing, but passing the raw image path is the cleanest method.
        results = self.detection_model(image_path)
        
        # Extract the bounding box coordinates from the YOLO results object
        # We move it to the CPU (just in case) and convert it to a standard NumPy array
        bounding_boxes = results[0].boxes.xyxy.cpu().numpy()
        
        # Extract the class labels (e.g., 'person', 'car', 'dog')
        class_ids = results[0].boxes.cls.cpu().numpy()
        
        # Combine them into a clean list of dictionaries for easier use later
        extracted_objects = []
        for i in range(len(bounding_boxes)):
            box = bounding_boxes[i]
            extracted_objects.append({
                "class_id": int(class_ids[i]),
                "coordinates": [int(box[0]), int(box[1]), int(box[2]), int(box[3])] # [x_min, y_min, x_max, y_max]
            })
            
        return extracted_objects

# --- How to test it ---
# vega = VegaProcessor()
# objects_found = vega.detect_objects("image1.jpg")
# print(objects_found)
def region_cropping(self, normalized_img, extracted_objects):
        """
        Takes the bounding box coordinates and slices the original image 
        to extract the cropped object patches.
        """
        cropped_patches = []

        for obj in extracted_objects:
            # Unpack the coordinates from our dictionary
            x_min, y_min, x_max, y_max = obj["coordinates"]

            # Slice the NumPy array! Remember: [Rows, Columns] -> [Y, X]
            patch = normalized_img[y_min:y_max, x_min:x_max]

            # We package the patch with its class_id so we don't lose track of what it is
            cropped_patches.append({
                "class_id": obj["class_id"],
                "patch": patch
            })

        return cropped_patches
