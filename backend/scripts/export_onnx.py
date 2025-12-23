from pathlib import Path

from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer


def main():
    model_id = "beomi/KcELECTRA-base"
    onnx_dir = Path("backend/models")
    onnx_dir.mkdir(parents=True, exist_ok=True)

    print("Loading tokenizer and exporting ONNX model...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = ORTModelForSequenceClassification.from_pretrained(
        model_id,
        export=True,
        provider="CPUExecutionProvider",
    )

    model.save_pretrained(onnx_dir)
    tokenizer.save_pretrained(onnx_dir / "tokenizer")
    print(f"Saved ONNX model to {onnx_dir}")


if __name__ == "__main__":
    main()
