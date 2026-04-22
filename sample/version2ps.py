from transformers import OwlViTProcessor, OwlViTForObjectDetection
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

TASK = "place flowers"
task_text = "a photo of a object to "+ TASK

IMAGE_PATH = "C:/Users/creat/BackUp/Coding projects/tosa-accelerator/PyAc/LivingRoomScene.png"
IMAGE = Image.open(IMAGE_PATH).convert("RGB")

LABELS = [
    "chair","sofa","bench","stool","seat","table","desk","platform",
    "vase","flower vase","pot","plant pot","container","bowl","cup","mug",
    "glass","wine glass","goblet","jug","pitcher","bottle",
    "spoon","teaspoon","tablespoon","ladle","scoop","fork",
    "knife","butter knife","kitchen knife","scissors","shears","tongs","spatula",
    "shovel","spade","garden shovel","hoe","rake","garden tool",
    "hammer","mallet","stick","rod","tool","opener","bottle opener","plier",
    "box","package","parcel","carton","book","plate","tray",
    "plant","watering can","sprayer","hose",
    "blanket","fire blanket","cloth","water"
]

INPUTS = processor(text=LABELS, images=IMAGE, return_tensors="pt")
OUTPUTS = model(**INPUTS)

TARGET_SIZES = torch.tensor([IMAGE.size[::-1]])
RESULTS = processor.post_process_grounded_object_detection(OUTPUTS, target_sizes=TARGET_SIZES)[0]

BOXES = RESULTS["boxes"]
SCORES = RESULTS["scores"]
LABEL_IDS = RESULTS["labels"]

best_score = -1
best_label = None
best_box = None

for box, det_score, label_id in zip(BOXES, SCORES, LABEL_IDS):

    if det_score < 0.2:
        continue

    x1, y1, x2, y2 = box.tolist()
    crop = IMAGE.crop((x1, y1, x2, y2))

    clip_inputs = clip_processor(
        text=[task_text],
        images=crop,
        return_tensors="pt",
        padding=True
    )

    clip_outputs = clip_model(**clip_inputs)
    clip_score = clip_outputs.logits_per_image.item()

    print(LABELS[label_id], "det:", det_score.item(), "clip:", clip_score)

    if clip_score > best_score:
        best_score = clip_score
        best_label = LABELS[label_id]
        best_box = box.tolist()

if best_score < 1.5:
    print("No suitable object found")
else:
    print("BEST:", best_label, best_score, best_box)