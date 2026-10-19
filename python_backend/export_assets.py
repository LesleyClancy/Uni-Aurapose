"""一次性脚本：导出 scaler/label 为 JSON，供 App 端侧 JS 引擎使用。"""
import json
import pickle
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "saved_models"
OUT = Path(__file__).parent.parent / "static" / "ai" / "scaler.json"

with open(MODEL_DIR / "scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open(MODEL_DIR / "label_encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

with open(MODEL_DIR / "model_params.json", "r", encoding="utf-8") as f:
    params = json.load(f)

payload = {
    "mean": [float(x) for x in scaler.mean_],
    "scale": [float(x) for x in scaler.scale_],
    "labels": list(encoder.classes_),
    "sequence_length": int(params.get("sequence_length", 30)),
    "input_dim": int(params.get("input_dim", 158)),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f)

print(f"written {OUT} dim={len(payload['mean'])} labels={payload['labels']}")
