#!/usr/bin/env bash
set -euo pipefail

# Script de configuración del entorno de experimentación
# Uso:
#   bash setup_env.sh

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="venv"

echo ">> Creando entorno virtual en '${VENV_DIR}'..."
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

echo ">> Activando entorno virtual..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo ">> Actualizando pip..."
python -m pip install --upgrade pip

echo ">> Instalando librerías requeridas..."
pip install pandas scikit-learn joblib matplotlib seaborn jupyter notebook

echo
echo "Entorno listo."
echo "Para activarlo manualmente en futuras sesiones ejecuta:"
echo "  source ${VENV_DIR}/bin/activate"
