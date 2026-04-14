import cv2
import numpy as np
from ultralytics import YOLO
from sentence_transformers import SentenceTransformer

class VegaProcessor:
    def __init__(self):
        print("Loading YOLOv8n model for vision...")
        self.detection_model = YOLO('yolov8n.pt') 
        
        # Load a lightweight, CPU-friendly text encoder for the Task Queries
        print("Loading MiniLM model for task encoding...")
        self.task_encoder_model = SentenceTransformer('all-MiniLM-L6-v2')

    # ... [Keep your existing resize_and_normalize method here] ...
    # ... [Keep your existing detect_objects method here] ...
    # ... [Keep your existing region_cropping method here] ...

    def task_encoder(self, task_query_text):
        """
        Converts the text of the DVCon query into a mathematical vector.
        """
        # The encode function automatically outputs a NumPy array
        task_vector = self.task_encoder_model.encode(task_query_text)
        
        return task_vector

    def execute_vega_pipeline(self, image_path, task_query_text):
        """
        This is the main function that runs everything in the VEGA block 
        and prepares the data for the BUS.
        """
        # 1. Image Processing Branch
        normalized_img = self.resize_and_normalize(image_path)
        extracted_objects = self.detect_objects(image_path)
        cropped_patches = self.region_cropping(normalized_img, extracted_objects)
        
        # 2. Task Encoding Branch
        task_vector = self.task_encoder(task_query_text)
        
        # The VEGA block is now finished! 
        # We package the Patches and the Vector to send over the BUS
        bus_payload = {
            "patches": cropped_patches,
            "task_vector": task_vector
        }
        
        return bus_payload

# --- How to test the complete VEGA block ---
# vega = VegaProcessor()
# query = "Find the fire extinguisher"
# data_for_bus = vega.execute_vega_pipeline("image1.jpg", query)
# print(f"Generated Vector Shape: {data_for_bus['task_vector'].shape}")
# print(f"Number of Patches generated: {len(data_for_bus['patches'])}")