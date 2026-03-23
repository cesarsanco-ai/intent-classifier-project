import os

import requests
import plotly.graph_objects as go
import streamlit as st

API_URL = os.getenv("BACKEND_PREDICT_URL", "http://localhost:8000/predict")

st.set_page_config(page_title="Smart Inbox AI", page_icon="📨", layout="wide")


def format_assistant_message(nb_label, nb_prob, svm_label, svm_prob):
    final_label = svm_label if svm_prob >= nb_prob else nb_label

    style_map = {
        "URGENTE": (
            "🚨 Detecto un caso URGENTE. "
            "Te recomiendo priorizar atención inmediata y escalar al equipo responsable."
        ),
        "SOPORTE": (
            "🛠️ Parece una solicitud de SOPORTE. "
            "Conviene abrir ticket técnico y responder con pasos de diagnóstico."
        ),
        "COMPRAS": (
            "🛒 Identifico una intención de COMPRAS. "
            "Lo ideal es derivar al flujo comercial o compartir plan/cotización."
        ),
        "SALUDO": (
            "🤝 Detecto un SALUDO. "
            "Puedes responder de forma cordial e invitar al usuario a detallar su necesidad."
        ),
    }

    friendly_text = style_map.get(final_label, "✅ Mensaje procesado.")
    detail = (
        f"\n\n**NB:** {nb_label} ({nb_prob * 100:.2f}%)"
        f"\n\n**SVM:** {svm_label} ({svm_prob * 100:.2f}%)"
        f"\n\n**Intención sugerida (mayor confianza):** `{final_label}`"
    )
    return friendly_text + detail


def render_confidence_chart(nb_prob, svm_prob):
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Naive Bayes", "SVM"],
                y=[nb_prob * 100, svm_prob * 100],
                marker_color=["#1f77b4", "#2ca02c"],
                text=[f"{nb_prob * 100:.2f}%", f"{svm_prob * 100:.2f}%"],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title="Confianza del último mensaje",
        yaxis_title="Confianza (%)",
        yaxis_range=[0, 100],
        margin=dict(l=20, r=20, t=50, b=20),
        height=330,
    )
    return fig


if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_scores" not in st.session_state:
    st.session_state.last_scores = None

st.title("Smart Inbox AI - Chat de Intenciones")
st.caption("Mensajería para clasificar: URGENTE, SOPORTE, COMPRAS y SALUDO.")

with st.sidebar:
    st.header("Panel de control")
    if st.button("Limpiar historial de chat"):
        st.session_state.messages = []
        st.session_state.last_scores = None
        st.rerun()

    if st.session_state.last_scores:
        nb_prob, svm_prob = st.session_state.last_scores
        st.plotly_chart(render_confidence_chart(nb_prob, svm_prob), use_container_width=True)
    else:
        st.info("Aún no hay predicciones para graficar.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Escribe un mensaje para clasificar...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = requests.post(API_URL, json={"text": prompt}, timeout=20)
        if response.status_code != 200:
            detail = response.json().get("detail", "Error desconocido en backend.")
            raise RuntimeError(detail)

        payload = response.json()
        nb = payload["naive_bayes"]
        svm = payload["svm"]

        nb_label, nb_prob = nb["label"], float(nb["probability"])
        svm_label, svm_prob = svm["label"], float(svm["probability"])

        assistant_text = format_assistant_message(nb_label, nb_prob, svm_label, svm_prob)
        st.session_state.last_scores = (nb_prob, svm_prob)

    except Exception as exc:
        assistant_text = (
            "❌ No pude obtener la predicción desde el backend.\n\n"
            f"Verifica que FastAPI esté corriendo en `{API_URL}`.\n\n"
            f"Detalle técnico: `{exc}`"
        )

    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
