import re
from pathlib import Path
from typing import Any

import joblib

# Lista manual de stopwords (idéntica al notebook)
STOPWORDS_ES = {
    "de", "la", "el", "y", "en", "a", "que", "los", "las", "por",
    "para", "con", "un", "una", "del", "al", "me", "mi", "es", "se"
}


def clean_text(text: str) -> str:
    """Limpieza de texto para clasificación en escenario controlado."""
    text = text.lower()
    text = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [token for token in text.split() if token not in STOPWORDS_ES]
    return " ".join(tokens)


def load_artifact(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    return joblib.load(path)
