from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

import numpy as np
import onnxruntime as ort
from transformers import AutoConfig, AutoTokenizer

# Fixed model ID (ignores env vars)
MODEL_ID = "sangrimlee/bert-base-multilingual-cased-nsmc"
MODEL_DIR = Path("backend/models")
MODEL_PATH = MODEL_DIR / "model.onnx"
TOKENIZER_PATH = MODEL_DIR / "tokenizer"


def analyze(text: str) -> Tuple[float, str]:
    """Return (score 0~1, label in negative/neutral/positive)."""
    warmup()
    session = _get_session()
    tokenizer = _get_tokenizer()
    labels = _get_labels()

    inputs = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        max_length=256,
        padding="max_length",
    )
    ort_inputs = {k: v.astype("int64") for k, v in inputs.items()}
    logits = session.run(None, ort_inputs)[0]
    probs = _softmax(logits[0])

    norm_labels = [str(lb).lower() for lb in labels]
    num_labels = len(norm_labels)
    max_idx = int(np.argmax(probs))

    # map label
    sentiment_label = _map_label(norm_labels, max_idx)

    # score: expected rating for 5-class, positive prob for others
    if num_labels == 5:
        weights = np.arange(1, num_labels + 1, dtype=np.float32)  # [1..5]
        expected = float(np.dot(probs, weights))
        score = float(np.clip(expected / weights[-1], 0.0, 1.0))
    else:
        pos_idx = _positive_index(norm_labels, num_labels)
        score = float(np.clip(probs[pos_idx], 0.0, 1.0))

    return score, sentiment_label


def warmup() -> None:
    _ensure_model_files()
    _get_session()
    _get_tokenizer()
    _get_labels()


def _positive_index(labels: List[str], num_labels: int) -> int:
    for i, lb in enumerate(labels):
        if "positive" in lb or "pos" in lb or "긍정" in lb:
            return i
    if num_labels == 3:
        return 2
    if num_labels >= 2:
        return 1
    return 0


def _map_label(labels: List[str], idx: int) -> str:
    lb = labels[idx] if idx < len(labels) else ""
    if any(k in lb for k in ["positive", "pos", "긍정"]):
        return "positive"
    if any(k in lb for k in ["neutral", "neu", "중립"]):
        return "neutral"
    if any(k in lb for k in ["negative", "neg", "부정"]):
        return "negative"

    # id2label like label_0, label_1
    if lb.startswith("label_"):
        try:
            n = int(lb.split("_")[1])
            if len(labels) == 3:
                if n == 2:
                    return "positive"
                if n == 1:
                    return "neutral"
                return "negative"
            if len(labels) >= 2:
                return "positive" if n == 1 else "negative"
        except Exception:
            pass

    if len(labels) == 3 and idx == 1:
        return "neutral"
    if len(labels) >= 2 and idx == 0:
        return "negative"
    return "positive"


def _softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


@lru_cache(maxsize=1)
def _get_session() -> ort.InferenceSession:
    providers = ["CPUExecutionProvider"]
    return ort.InferenceSession(str(MODEL_PATH), providers=providers)


@lru_cache(maxsize=1)
def _get_tokenizer() -> AutoTokenizer:
    return AutoTokenizer.from_pretrained(TOKENIZER_PATH)


@lru_cache(maxsize=1)
def _get_labels() -> List[str]:
    try:
        cfg = AutoConfig.from_pretrained(MODEL_DIR)
        id2label = getattr(cfg, "id2label", None)
        if id2label:
            return [label for _, label in sorted(id2label.items(), key=lambda x: int(x[0]))]
    except Exception:
        pass
    return ["negative", "positive"]


def _ensure_model_files() -> None:
    if MODEL_PATH.exists() and TOKENIZER_PATH.exists():
        return
    _export_onnx()


def download_model() -> None:
    """Render build step helper: pre-download and export ONNX artifacts."""
    warmup()


def _export_onnx() -> None:
    try:
        from optimum.onnxruntime import ORTModelForSequenceClassification
    except ImportError as exc:
        raise RuntimeError("optimum.onnxruntime is required. Install with: pip install 'optimum[onnxruntime]'") from exc

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    TOKENIZER_PATH.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = ORTModelForSequenceClassification.from_pretrained(
        MODEL_ID,
        export=True,
        provider="CPUExecutionProvider",
    )

    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(TOKENIZER_PATH)
