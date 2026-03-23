import random
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from ml_utils import clean_text

SEED = 42
random.seed(SEED)


def build_synthetic_dataset() -> pd.DataFrame:
    urgente_texts = [
        "es urgente necesito ayuda ahora",
        "tengo una emergencia con el servicio",
        "prioridad alta por favor responder ya",
        "problema critico necesito solucion inmediata",
        "requiero atencion urgente hoy mismo",
        "se cayo el sistema y es urgente",
        "no puedo operar necesito soporte urgente",
        "incidencia grave resolver en este momento",
        "es un caso urgente para el equipo",
        "por favor atiendan esto de inmediato",
    ]
    soporte_texts = [
        "necesito soporte tecnico para mi cuenta",
        "pueden ayudarme con este error",
        "como configuro la aplicacion correctamente",
        "tengo dudas sobre el funcionamiento",
        "requiero asistencia para instalar el sistema",
        "el modulo no responde necesito soporte",
        "me explican como recuperar mi usuario",
        "ayuda con la configuracion del perfil",
        "tengo un problema tecnico recurrente",
        "podrian orientarme con este inconveniente",
    ]
    compras_texts = [
        "quiero conocer el precio del plan premium",
        "me interesa comprar una licencia anual",
        "podrian enviar cotizacion del servicio",
        "cual es el costo de la suscripcion",
        "necesito informacion para realizar una compra",
        "quiero adquirir el paquete empresarial",
        "tienen descuento por volumen",
        "me comparten los planes disponibles",
        "como hago el proceso de compra",
        "deseo contratar el servicio este mes",
    ]
    saludo_texts = [
        "hola buenos dias",
        "buenas tardes como estan",
        "hola equipo gracias por su ayuda",
        "que tal espero que esten bien",
        "saludos cordiales",
        "hola necesito orientacion general",
        "buen dia",
        "hola me presento soy cliente nuevo",
        "mucho gusto en contactarles",
        "hola hola",
    ]

    # Replicamos frases para tener dataset balanceado y compacto (50 por clase)
    data = (
        [(t, "URGENTE") for t in urgente_texts * 5]
        + [(t, "SOPORTE") for t in soporte_texts * 5]
        + [(t, "COMPRAS") for t in compras_texts * 5]
        + [(t, "SALUDO") for t in saludo_texts * 5]
    )
    random.shuffle(data)
    return pd.DataFrame(data, columns=["texto", "etiqueta"])


def main():
    df = build_synthetic_dataset()
    df["texto_limpio"] = df["texto"].apply(clean_text)

    X = df["texto_limpio"].tolist()
    y = df["etiqueta"].tolist()

    vectorizer = TfidfVectorizer()
    X_vec = vectorizer.fit_transform(X)

    nb_model = MultinomialNB()
    svm_model = SVC(kernel="linear", probability=True, random_state=SEED)

    nb_model.fit(X_vec, y)
    svm_model.fit(X_vec, y)

    out_dir = Path(__file__).resolve().parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(nb_model, out_dir / "nb_model.pkl")
    joblib.dump(svm_model, out_dir / "svm_model.pkl")
    joblib.dump(vectorizer, out_dir / "vectorizer.pkl")

    print("Modelos exportados en backend/models/:")
    print("- nb_model.pkl")
    print("- svm_model.pkl")
    print("- vectorizer.pkl")


if __name__ == "__main__":
    main()
