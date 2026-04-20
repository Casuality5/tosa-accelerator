from transformers import OwlViTProcessor, OwlViTForObjectDetection
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")



IMAGE_PATH = "C:/Users/creat/BackUp/Coding projects/tosa-accelerator/PyAc/image.png"




IMAGE = Image.open(IMAGE_PATH)

LABELS = ["Clock","Chair","Desk"]

INPUTS = processor(text = LABELS, images = IMAGE, return_tensors= "pt")

OUTPUTS = model(**INPUTS)


TARGET_SIZES = torch.tensor([IMAGE.size[::-1]])

RESULTS = processor.post_process_grounded_object_detection(OUTPUTS, target_sizes=TARGET_SIZES)[0]


BOXES = RESULTS["boxes"]

SCORES = RESULTS["scores"]

LABEL_IDS = RESULTS["labels"]


for box, score, label_id in zip(BOXES, SCORES, LABEL_IDS):
    print(LABELS[label_id], score.item(), box.tolist())

          
