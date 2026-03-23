from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ml_utils import clean_text, load_artifact

app = FastAPI(title="Smart Inbox AI API", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

CLASSES = ["URGENTE", "SOPORTE", "COMPRAS", "SALUDO"]

try:
    nb_model = load_artifact(MODELS_DIR / "nb_model.pkl")
    svm_model = load_artifact(MODELS_DIR / "svm_model.pkl")
    vectorizer = load_artifact(MODELS_DIR / "vectorizer.pkl")
except FileNotFoundError as exc:
    nb_model = None
    svm_model = None
    vectorizer = None
    MODEL_LOAD_ERROR = str(exc)
else:
    MODEL_LOAD_ERROR = ""


class PredictRequest(BaseModel):
    text: str


def _predict_with_model(model, vectorized_text) -> Dict[str, float]:
    proba = model.predict_proba(vectorized_text)[0]
    idx = int(proba.argmax())
    pred_label = model.classes_[idx]
    pred_conf = float(proba[idx])
    return {
        "label": pred_label,
        "probability": pred_conf
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictRequest):
    if MODEL_LOAD_ERROR:
        raise HTTPException(
            status_code=500,
            detail=(
                "Los modelos no están cargados correctamente. "
                f"Detalle: {MODEL_LOAD_ERROR}"
            ),
        )

    original_text = payload.text.strip()
    if not original_text:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")
    if len(original_text) < 4:
        raise HTTPException(
            status_code=400,
            detail="El texto es muy corto. Ingresa al menos 4 caracteres.",
        )

    cleaned_text = clean_text(original_text)
    if not cleaned_text:
        raise HTTPException(
            status_code=400,
            detail="El texto no contiene términos útiles tras la limpieza.",
        )

    X = vectorizer.transform([cleaned_text])
    nb_result = _predict_with_model(nb_model, X)
    svm_result = _predict_with_model(svm_model, X)

    return {
        "input_text": original_text,
        "cleaned_text": cleaned_text,
        "naive_bayes": nb_result,
        "svm": svm_result,
        "supported_classes": CLASSES,
    }
