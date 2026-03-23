# Smart Inbox AI - Clasificador de Intenciones

Proyecto de portafolio, usando Naive Bayes (NB) y Maquina de Soporte Vectorial (SVM) para clasificar mensajes en 4 intenciones:

- `URGENTE`
- `SOPORTE`
- `COMPRAS`
- `SALUDO`

Incluye:
- un notebook de experimentación (`research/`)
- una app local full-stack (`smart-inbox-ai/`) con backend FastAPI y frontend Streamlit.

## Demo

<p align="center">
  <img src="assets/demo.png" alt="Demo de Smart Inbox AI clasificando intenciones en tiempo real" width="900" />
</p>

<p align="center">
  Interfaz principal del clasificador mostrando predicciones de intención y nivel de confianza por modelo.
</p>

## Estructura del proyecto

```text
PROY_CLASIFICADOR_INTENCIONES/
├── research/
│   └── model_experimentation.ipynb
├── smart-inbox-ai/
│   ├── backend/
│   │   ├── main.py
│   │   ├── ml_utils.py
│   │   ├── train_models.py
│   │   ├── entrypoint.sh
│   │   ├── Dockerfile
│   │   └── models/              # generado localmente (.pkl)
│   ├── frontend/
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   ├── requirements.txt
│   └── .env.example
├── setup_env.sh
└── .gitignore
```

## Arquitectura con Docker Compose

El stack `smart-inbox-ai/` se ejecuta con 2 servicios y 1 volumen persistente:

- `backend` (FastAPI + Uvicorn): expone API y healthcheck en el puerto interno `8000`.
- `frontend` (Streamlit): UI web en el puerto interno `8501`.
- `backend_models` (volumen): persiste `backend/models` para evitar reentrenar modelos en cada reinicio.

Flujo:
1. El usuario abre `frontend`.
2. `frontend` llama a `http://backend:8000/predict` dentro de la red de Compose.
3. `backend` responde la intención y las probabilidades por modelo.

Detalles operativos:
- `frontend` espera a que `backend` esté saludable (`depends_on` con `condition: service_healthy`).
- El backend entrena modelos durante el build de imagen (`backend/Dockerfile`).
- Si el volumen de modelos está vacío al arrancar, se reentrena automáticamente (`backend/entrypoint.sh`).
- Los puertos externos son configurables con `BACKEND_PORT` y `FRONTEND_PORT`.

## Vía rápida (producción/demo con Docker)

Si acabas de clonar el repo, este es el camino recomendado.

### Requisitos

- Docker + Docker Compose plugin
- macOS / Linux / Windows

### Levantar el stack

Desde `smart-inbox-ai/`:

```bash
docker compose up --build -d
```

> `--build` es importante: durante ese build el backend ejecuta `train_models.py` y deja listos los artefactos iniciales.

Si tienes puertos ocupados, puedes sobrescribirlos:

```bash
BACKEND_PORT=8002 FRONTEND_PORT=8502 docker compose up --build -d
```

Servicios:
- Frontend: [http://localhost:${FRONTEND_PORT:-8501}](http://localhost:8501)
- Backend docs: [http://localhost:${BACKEND_PORT:-8000}/docs](http://localhost:8000/docs)
- Backend health: [http://localhost:${BACKEND_PORT:-8000}/health](http://localhost:8000/health)
  
> Si cambias `BACKEND_PORT` o `FRONTEND_PORT`, ajusta estas URLs al puerto elegido.

Notas de operación:
- El backend ejecuta `python /app/backend/train_models.py` durante el build (`backend/Dockerfile`).
- Al iniciar, si faltan artefactos por volumen vacío o limpieza previa, se regeneran automáticamente (`backend/entrypoint.sh`).
- Los modelos se persisten en un volumen Docker (`backend_models`) para no reentrenar en cada restart.
- El frontend usa `BACKEND_PREDICT_URL=http://backend:8000/predict` dentro de la red interna de Compose.

Apagar stack:

```bash
docker compose down
```

Apagar stack y eliminar volumen de modelos:

```bash
docker compose down -v
```

## Flujo local (opcional, para desarrollo/experimentos)

Este flujo solo es necesario si quieres ejecutar backend/frontend fuera de Docker o experimentar manualmente con entrenamiento.

### Requisitos

- Python 3.11+
- macOS / Linux / Windows (con equivalentes de comandos)

### 1) Preparar entorno

Desde la raíz del repositorio:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r smart-inbox-ai/requirements.txt
```

> Opcional: también puedes usar `bash setup_env.sh` para instalar dependencias de notebook.

### 2) Generar modelos (opcional, artefactos `.pkl`)

```bash
cd smart-inbox-ai
python backend/train_models.py
```

Se crearán:
- `smart-inbox-ai/backend/models/nb_model.pkl`
- `smart-inbox-ai/backend/models/svm_model.pkl`
- `smart-inbox-ai/backend/models/vectorizer.pkl`

### 3) Ejecutar backend (FastAPI)

En una terminal:

```bash
source venv/bin/activate
cd smart-inbox-ai/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verificación:
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

### 4) Ejecutar frontend (Streamlit)

En otra terminal:

```bash
source venv/bin/activate
cd smart-inbox-ai/frontend
streamlit run app.py
```

Abrir en navegador:
- [http://localhost:8501](http://localhost:8501)

## Configuración por variables de entorno

El frontend permite configurar el endpoint del backend:

```bash
export BACKEND_PREDICT_URL=http://localhost:8000/predict
```

Referencia: `smart-inbox-ai/.env.example`.

## Probar API rápidamente

```bash
curl -X POST "http://localhost:${BACKEND_PORT:-8000}/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, necesito saber el precio del soporte urgente"}'
```

## Checklist de revisión rápida

1. Validar contenedores y salud:
   ```bash
   docker compose ps
   ```
2. Revisar logs de arranque (backend/frontend):
   ```bash
   docker compose logs -f backend frontend
   ```
3. Probar healthcheck backend:
   ```bash
   curl http://localhost:${BACKEND_PORT:-8000}/health
   ```
4. Probar predicción por API:
   ```bash
   curl -X POST "http://localhost:${BACKEND_PORT:-8000}/predict" \
     -H "Content-Type: application/json" \
     -d '{"text":"Necesito ayuda urgente con mi cuenta"}'
   ```
5. Verificar UI en navegador:
   - Abrir [http://localhost:${FRONTEND_PORT:-8501}](http://localhost:8501)
   - Enviar un mensaje y confirmar respuesta del asistente + gráfica de confianza.


## Notas

- Los modelos `.pkl` están ignorados por `.gitignore` para evitar subir binarios generados localmente.
- Para levantar el proyecto en una máquina nueva, basta con `docker compose up --build -d` desde `smart-inbox-ai/`.
- Los `.pkl` locales pueden mantenerse para pruebas y experimentación manual con `train_models.py`, pero no son requisito para ejecutar el stack con Docker.
