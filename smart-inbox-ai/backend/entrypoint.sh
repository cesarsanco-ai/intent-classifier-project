#!/usr/bin/env sh
set -e

MODELS_DIR="/app/backend/models"

if [ ! -f "$MODELS_DIR/nb_model.pkl" ] || [ ! -f "$MODELS_DIR/svm_model.pkl" ] || [ ! -f "$MODELS_DIR/vectorizer.pkl" ]; then
  echo "Modelos no encontrados. Entrenando artefactos iniciales..."
  python /app/backend/train_models.py
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
