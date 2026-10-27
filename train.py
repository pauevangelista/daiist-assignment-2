"""Assignment 2 training pipeline, stage 1: download, finetune, save weights."""
import os
import shutil
from pathlib import Path

import torch
from roboflow import Roboflow
from ultralytics import YOLO

from api_key import load_api_key

# Dataset (also recorded in REPORT.md)
WORKSPACE = "roboflow-universe-projects"
PROJECT = "mask-wearing-iskms"
VERSION = 6

# Settings. QUICK=1 is a smoke test: tiny subset, 2 epochs, just to prove the pipeline runs.
QUICK = os.environ.get("QUICK") == "1"
MODEL = "yolo11n.pt"
EPOCHS = 2 if QUICK else 40
FRACTION = 0.1 if QUICK else 1.0
IMGSZ = 640
BATCH = 16
SEED = 0

DATA_DIR = Path("data")
WEIGHTS_DIR = Path("weights")


def pick_device():
    if torch.cuda.is_available():
        return 0
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def download_dataset() -> Path:
    ds = (
        Roboflow(api_key=load_api_key())
        .workspace(WORKSPACE)
        .project(PROJECT)
        .version(VERSION)
        .download("yolov8", location=str(DATA_DIR), overwrite=False)
    )
    return Path(ds.location) / "data.yaml"


def finetune(data_yaml: Path) -> Path:
    name = "mask_quick" if QUICK else "mask"
    model = YOLO(MODEL)
    model.train(
        data=str(data_yaml),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        seed=SEED,
        fraction=FRACTION,
        device=pick_device(),
        project="runs",
        name=name,
        exist_ok=True,
        plots=False,
    )
    best = Path(model.trainer.best)
    WEIGHTS_DIR.mkdir(exist_ok=True)
    target = WEIGHTS_DIR / ("best_quick.pt" if QUICK else "best.pt")
    shutil.copy(best, target)
    return target


def main():
    data_yaml = download_dataset()
    weights = finetune(data_yaml)
    print(f"Saved weights to {weights}")


if __name__ == "__main__":
    main()
