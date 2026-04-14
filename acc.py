import numpy as np

class AcceleratorSimulator:
    def __init__(self):
        # Here you would load the pre-trained vision model (like MobileNet or ResNet)
        # to act as your PE Array for extracting features from the cropped patches.
        print("Initializing Accelerator hardware simulation...")
        pass

    def hardware_relu(self, feature_vector):
        """Simulates the ReLU hardware block: Clips Negative Numbers to 0."""
        return np.maximum(0, feature_vector)

    def simulate_pe_array_and_gap(self, image_patch):
        """
        Simulates the Systolic MAC Grid and GAP.
        Converts a 2D/3D image patch into a 1D Visual Embedding Vector.
        """
        # --- PLACEHOLDER ---
        # In a real implementation, you will pass the 'image_patch' through a CNN here.
        # For now, we generate a random dummy 1D vector to simulate the hardware output.
        # Note: The output size MUST match your Task Vector size (e.g., 384)
        raw_visual_vector = np.random.rand(384) 
        
        # Pass through hardware ReLU
        activated_vector = self.hardware_relu(raw_visual_vector)
        
        return activated_vector

    def similarity_engine(self, visual_vector, task_vector):
        """Simulates the Vector Dot Product in hardware."""
        # A simple dot product determines how similar the image patch is to the text query
        suitability_score = np.dot(visual_vector, task_vector)
        return suitability_score

    def process_bus_data(self, bus_payload):
        """
        The main DMA Controller/Data Dispatcher logic.
        Receives data from VEGA and routes it through the accelerator.
        """
        patches = bus_payload["patches"]
        task_vector = bus_payload["task_vector"]
        
        suitability_scores = []
        object_ids = []

        # Iterate through the patches stored in the SRAM block
        for item in patches:
            patch_matrix = item["patch"]
            obj_id = item["class_id"]
            
            # 1. Generate the Visual Embedding Vector (PE Array -> ReLU -> GAP)
            visual_vector = self.simulate_pe_array_and_gap(patch_matrix)
            
            # 2. Compute the Dot Product against the Task Vector
            score = self.similarity_engine(visual_vector, task_vector)
            
            suitability_scores.append(score)
            object_ids.append(obj_id)

        # Send these back up to VEGA's "Select Ranking Module"
        return suitability_scores, object_ids

# --- Integration Test ---
# accelerator = AcceleratorSimulator()
# scores, ids = accelerator.process_bus_data(data_for_bus)
# print(f"Object IDs: {ids}")
# print(f"Suitability Scores: {scores}")