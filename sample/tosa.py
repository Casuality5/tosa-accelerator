#!/usr/bin/env python3
"""
tosa.py  —  Task-Driven Object Selection Pipeline
DVCon India 2026 | Stage 2A

Single-file. CPU-only. No training. No hardware simulation.
Usage:
    python tosa.py --image path/to/image.jpg --task "serve wine"
    python tosa.py --image path/to/image.jpg --task "sit comfortably" --debug
    python tosa.py --image path/to/image.jpg --task "dig hole" --fallback --threshold 0.25
    python tosa.py --image path/to/image.jpg --task "serve wine" --json
    python tosa.py --list-tasks
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Task keyword map  (high-level concepts, NOT fixed COCO label lists)
# ---------------------------------------------------------------------------
TASK_KEYWORDS: dict[str, list[str]] = {
    "step on something":        ["platform", "step", "furniture", "support", "flat"],
    "sit comfortably":          ["seat", "chair", "furniture", "cushion", "comfort"],
    "place flowers":            ["container", "vase", "pot", "vessel", "holder"],
    "get potatoes out of fire": ["grip", "tong", "scoop", "handle", "kitchen"],
    "water plant":              ["pour", "water", "container", "jug", "liquid"],
    "get lemon out of tea":     ["spoon", "ladle", "utensil", "scoop", "pick"],
    "dig hole":                 ["shovel", "dig", "spade", "tool", "garden"],
    "open bottle of beer":      ["opener", "lever", "key", "pry", "tool"],
    "open parcel":              ["cut", "blade", "knife", "scissors", "sharp"],
    "serve wine":               ["drink", "glass", "container", "vessel", "cup"],
    "pour sugar":               ["spoon", "scoop", "ladle", "bowl", "container"],
    "smear butter":             ["knife", "spread", "blade", "utensil", "flat"],
    "extinguish fire":          ["extinguish", "blanket", "cover", "water", "smother"],
    "pound carpet":             ["hammer", "mallet", "beat", "heavy", "tool"],
}

# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------
@dataclass
class Detection:
    label: str
    confidence: float
    bbox: tuple[float, float, float, float]   # x1, y1, x2, y2

@dataclass
class ScoredDetection:
    detection: Detection
    semantic_sim: float
    keyword_sim: float
    final_score: float


# ---------------------------------------------------------------------------
# Module-level singletons (lazy-loaded)
# ---------------------------------------------------------------------------
_yolo_model   = None
_embed_model  = None
_embed_cache: dict[str, np.ndarray] = {}


def _get_yolo():
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        logger.info("Loading YOLOv8n (CPU) ...")
        _yolo_model = YOLO("yolov8n.pt")
    return _yolo_model


def _get_embedder():
    """
    Try sentence-transformers/all-MiniLM-L6-v2.
    Falls back to a lightweight offline TF-IDF embedder if HuggingFace
    is unreachable (restricted network / edge environment).
    """
    global _embed_model
    if _embed_model is not None:
        return _embed_model
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformer (CPU) ...")
        _embed_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
        )
        logger.info("sentence-transformer loaded OK")
    except Exception as exc:
        logger.warning(
            "sentence-transformers unavailable (%s); using offline TF-IDF fallback.", exc
        )
        _embed_model = _TfidfEmbedder()
    return _embed_model


class _TfidfEmbedder:
    """
    Minimal offline embedder — character n-gram bag-of-words.
    No downloads required. Less accurate than sentence-transformers
    but deterministic and fully self-contained.
    """
    def __init__(self, ngram: int = 3):
        self.ngram = ngram
        self._vocab: dict[str, int] = {}

    def _ngrams(self, text: str) -> list[str]:
        text = text.lower().replace("-", " ").replace("_", " ")
        tokens = text.split()
        grams: list[str] = []
        for tok in tokens:
            tok = " " + tok + " "
            grams += [tok[i:i + self.ngram] for i in range(len(tok) - self.ngram + 1)]
        return grams

    def encode(self, text: str, **kwargs) -> np.ndarray:
        grams = self._ngrams(text)
        if not grams:
            return np.zeros(512, dtype=np.float32)
        for g in grams:
            if g not in self._vocab:
                self._vocab[g] = len(self._vocab)
        dim = max(len(self._vocab), 512)
        vec = np.zeros(dim, dtype=np.float32)
        for g in grams:
            vec[self._vocab[g]] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec


# ---------------------------------------------------------------------------
# Core pipeline functions
# ---------------------------------------------------------------------------

def detect(image_path: str) -> list[Detection]:
    """Run YOLOv8 on image_path and return a list of Detection objects."""
    model = _get_yolo()
    results = model(image_path, verbose=False, device="cpu")
    detections: list[Detection] = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            cls_id = int(box.cls[0].item())
            label  = model.names[cls_id]
            conf   = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(Detection(label=label, confidence=conf,
                                        bbox=(x1, y1, x2, y2)))
    logger.debug("Raw detections: %s",
                 [(d.label, round(d.confidence, 3)) for d in detections])
    return detections


def embed(text: str) -> np.ndarray:
    """Return a unit-normalised embedding vector for text (cached)."""
    if text not in _embed_cache:
        model = _get_embedder()
        vec = model.encode(text)
        _embed_cache[text] = np.asarray(vec, dtype=np.float32)
    return _embed_cache[text]


def semantic_similarity(a: str, b: str) -> float:
    """Cosine similarity between embeddings of a and b, clipped to [0, 1]."""
    ea, eb = embed(a), embed(b)
    if ea.shape != eb.shape:
        dim = max(len(ea), len(eb))
        ea  = np.pad(ea, (0, dim - len(ea)))
        eb  = np.pad(eb, (0, dim - len(eb)))
    return max(0.0, float(np.dot(ea, eb)))


def keyword_score(label: str, task: str) -> float:
    """
    Max cosine similarity between label and each concept keyword for task.
    Keywords are high-level concepts in TASK_KEYWORDS — not fixed COCO labels.
    """
    task_key = _normalise_task(task)
    keywords = TASK_KEYWORDS.get(task_key, [])
    if not keywords:
        return 0.0
    return max(semantic_similarity(label, kw) for kw in keywords)


def score_object(
    det: Detection,
    task: str,
    w_semantic: float = 0.50,
    w_keyword:  float = 0.30,
    w_conf:     float = 0.20,
    relevance_threshold: float = 0.30,
) -> ScoredDetection:
    """
    Compute task-aware score for a single Detection.

    score = 0.50 * semantic_sim(task, label)
          + 0.30 * max_keyword_sim(label, task_keywords)
          + 0.20 * detection_confidence

    Relevance gate: if BOTH sem_sim AND keyword_sim < threshold, score = 0.
    This prevents unrelated objects (e.g. 'chair' for 'serve wine') from
    winning purely on detection confidence.
    """
    sem = semantic_similarity(task, det.label)
    kw  = keyword_score(det.label, task)

    if sem < relevance_threshold and kw < relevance_threshold:
        final = 0.0
    else:
        final = w_semantic * sem + w_keyword * kw + w_conf * det.confidence

    return ScoredDetection(detection=det, semantic_sim=sem,
                           keyword_sim=kw, final_score=final)


def select_best(
    scored: list[ScoredDetection],
    fallback_to_highest_conf: bool = False,
) -> Optional[ScoredDetection]:
    """
    Return the ScoredDetection with the highest final_score.
    Returns None if all scores are 0, unless fallback_to_highest_conf=True.
    """
    if not scored:
        return None
    best = max(scored, key=lambda s: s.final_score)
    if best.final_score == 0.0:
        if fallback_to_highest_conf:
            best = max(scored, key=lambda s: s.detection.confidence)
            logger.warning(
                "No object passed relevance gate; falling back to highest-confidence: %s",
                best.detection.label,
            )
            return best
        return None
    return best


# ---------------------------------------------------------------------------
# High-level entry point (importable)
# ---------------------------------------------------------------------------

def run(
    image_path: str,
    task: str,
    relevance_threshold: float = 0.30,
    fallback: bool = False,
    debug: bool = False,
) -> dict:
    """
    Full pipeline: (image_path, task) -> result dict.

    Returns
    -------
    {
        "label": str,           # best object label, or "none"
        "score": float,
        "bbox":  tuple | None,  # (x1, y1, x2, y2)
        "all":   list[dict],    # all scored detections for analysis
    }
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")
    else:
        logging.basicConfig(level=logging.INFO,  format="%(levelname)s | %(message)s")

    detections = detect(image_path)

    if not detections:
        logger.info("No objects detected in image.")
        return {"label": "none", "score": 0.0, "bbox": None, "all": []}

    scored = [
        score_object(d, task, relevance_threshold=relevance_threshold)
        for d in detections
    ]

    if debug:
        print("\n── All detections (sorted by final score) ──")
        for s in sorted(scored, key=lambda x: -x.final_score):
            gated = "GATED" if s.final_score == 0 else "ok"
            print(f"  {s.detection.label:20s}  "
                  f"conf={s.detection.confidence:.3f}  "
                  f"sem={s.semantic_sim:.3f}  "
                  f"kw={s.keyword_sim:.3f}  "
                  f"final={s.final_score:.4f}  [{gated}]")
        print()

    best = select_best(scored, fallback_to_highest_conf=fallback)

    if best is None:
        return {"label": "none", "score": 0.0, "bbox": None,
                "all": _serialise(scored)}

    return {
        "label": best.detection.label,
        "score": round(best.final_score, 4),
        "bbox":  best.detection.bbox,
        "all":   _serialise(scored),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_task(task: str) -> str:
    """Match task string to a key in TASK_KEYWORDS (fuzzy)."""
    task_lower = task.lower().strip()
    for key in TASK_KEYWORDS:
        if key in task_lower or task_lower in key:
            return key
    # Fallback: pick the key whose embedding is closest
    best_key, best_sim = "", -1.0
    for key in TASK_KEYWORDS:
        s = semantic_similarity(task_lower, key)
        if s > best_sim:
            best_sim, best_key = s, key
    logger.debug("Task '%s' matched to '%s' (sim=%.3f)", task, best_key, best_sim)
    return best_key


def _serialise(scored: list[ScoredDetection]) -> list[dict]:
    return [
        {
            "label":      s.detection.label,
            "confidence": round(s.detection.confidence, 4),
            "sem_sim":    round(s.semantic_sim, 4),
            "kw_sim":     round(s.keyword_sim, 4),
            "score":      round(s.final_score, 4),
            "bbox":       s.detection.bbox,
        }
        for s in sorted(scored, key=lambda x: -x.final_score)
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Task-Driven Object Selection  |  DVCon India 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tosa.py --image kitchen.jpg --task "serve wine"
  python tosa.py --image room.jpg    --task "sit comfortably" --debug
  python tosa.py --image desk.jpg    --task "smear butter" --fallback --threshold 0.25
  python tosa.py --image img.jpg     --task "dig hole" --json
  python tosa.py --list-tasks
        """,
    )
    p.add_argument("--image",      help="Path to input image")
    p.add_argument("--task",       help="Task string, e.g. \"serve wine\"")
    p.add_argument("--threshold",  type=float, default=0.30,
                   help="Relevance gate threshold (default: 0.30)")
    p.add_argument("--fallback",   action="store_true",
                   help="Return highest-confidence detection if nothing passes gate")
    p.add_argument("--debug",      action="store_true",
                   help="Print per-object scores")
    p.add_argument("--json",       action="store_true",
                   help="Output full result as JSON")
    p.add_argument("--list-tasks", action="store_true",
                   help="List all registered tasks and exit")
    return p


def main():
    parser = _build_parser()
    args   = parser.parse_args()

    if args.list_tasks:
        print("\nRegistered tasks and keyword concepts:\n")
        for task, kws in TASK_KEYWORDS.items():
            print(f"  {task}")
            print(f"    keywords: {', '.join(kws)}\n")
        sys.exit(0)

    if not args.image or not args.task:
        parser.print_help()
        sys.exit(1)

    result = run(
        image_path=args.image,
        task=args.task,
        relevance_threshold=args.threshold,
        fallback=args.fallback,
        debug=args.debug,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        label = result["label"]
        score = result["score"]
        bbox  = result["bbox"]
        print(f"\n{'='*50}")
        print(f"  Task   : {args.task}")
        print(f"  Result : {label}")
        print(f"  Score  : {score:.4f}")
        if bbox:
            x1, y1, x2, y2 = bbox
            print(f"  BBox   : ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f})")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    main()