# streamlit_app.py
"""
Interface de démo Streamlit pour tester rapidement les fonctionnalités clés :
- Upload de fichiers (images, CSV/Excel, texte, PDF, autres)
- Formulaires (inputs variés, validation, form_key)
- Éditeur de données + graphiques
- Caméra (webcam)
- Espace Chat (st.chat_input / st.chat_message)
- Session state & cache (st.session_state, st.cache_data)
- Notifications, statut, progression, toasts

▶️ Lancer :
    pip install streamlit pandas numpy
    streamlit run streamlit_app.py
"""

from __future__ import annotations
import io
import time
from datetime import date, time as dtime
from typing import List

import numpy as np
import pandas as pd
import streamlit as st

APP_TITLE = "🧪 Streamlit — Playground de fonctionnalités"

# ---------------------------
# Utils
# ---------------------------

def _is_text(b: bytes) -> bool:
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False

@st.cache_data(show_spinner=False)
def fake_slow_sum(numbers: List[float]) -> float:
    """Exemple de fonction mise en cache (simule un calcul lent)."""
    time.sleep(2)
    return float(np.sum(numbers))

# ---------------------------
# Sections (routées par la sidebar)
# ---------------------------

def render_home():
    st.title(APP_TITLE)
    st.write(
        "Bienvenue ! Sélectionnez une section dans la barre latérale pour tester les composants Streamlit.")

    st.markdown(
        """
        **Ce que vous pouvez essayer :**
        - 📤 *Upload* : importez plusieurs fichiers à la fois et prévisualisez-les
        - 📝 *Formulaires* : saisies, validations et envoi groupé
        - 🧮 *Données & Graphiques* : éditez un DataFrame et tracez un graphe
        - 📷 *Caméra* : capturez une image via la webcam
        - 💬 *Chat* : testez l'interface de conversation Streamlit
        - 🧠 *État & Cache* : jouez avec `st.session_state` et `st.cache_data`
        - 🔔 *Notifications* : barres de progression, `st.status`, `st.toast`
        """
    )

    with st.expander("Astuce : structure type d'une app Streamlit"):
        st.code(
            """
            import streamlit as st

            def main():
                st.sidebar.title("Navigation")
                page = st.sidebar.radio("Aller à", ["Accueil", "Upload", ...])
                if page == "Accueil":
                    ...
                elif page == "Upload":
                    ...
            if __name__ == "__main__":
                main()
            """,
            language="python",
        )


def render_upload():
    st.header("📤 Upload de fichiers via la page web")
    st.caption("Déposez un ou plusieurs fichiers ci-dessous — prévisualisation automatique selon le type.")

    files = st.file_uploader(
        "Choisir des fichiers",
        accept_multiple_files=True,
        type=None,  # autorise tout
        help="Vous pouvez glisser-déposer ou cliquer pour sélectionner."
    )

    if not files:
        st.info("Aucun fichier sélectionné pour le moment.")
        return

    for f in files:
        st.divider()
        st.subheader(f"Fichier : {f.name}")
        st.write(f"Taille : {f.size} octets \| Type MIME : {f.type or 'inconnu'}")

        content = f.read()
        # Important : remettre le curseur du buffer si on veut relire plus tard
        f.seek(0)

        # Affichage conditionnel selon l'extension ou MIME
        if f.type and f.type.startswith("image/"):
            st.image(content, caption=f.name, use_container_width=True)

        elif f.type in ("text/plain",) or (f.type in (None, "application/octet-stream") and _is_text(content)):
            st.text_area("Aperçu texte (UTF‑8)", content.decode("utf-8"), height=200)

        elif f.type in ("text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") or f.name.lower().endswith((".csv", ".xls", ".xlsx")):
            try:
                if f.name.lower().endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                st.dataframe(df, use_container_width=True)
                st.download_button("Télécharger en CSV (copie)", df.to_csv(index=False).encode("utf-8"), file_name=f"copy_{f.name.split('.')[0]}.csv")
            except Exception as e:
                st.error(f"Impossible de lire le tableau : {e}")

        elif f.type in ("application/pdf",) or f.name.lower().endswith(".pdf"):
            st.info("PDF reçu — aperçu natif minimal dans Streamlit. Vous pouvez le télécharger ci‑dessous.")
            st.download_button("Télécharger le PDF", data=content, file_name=f.name)

        else:
            st.warning("Type non reconnu. Téléchargement brut disponible.")
            st.download_button("Télécharger le fichier (brut)", data=content, file_name=f.name)


def render_forms():
    st.header("📝 Formulaires & validations")
    st.write("Démonstration d'un formulaire complet avec envoi groupé.")

    with st.form("demo_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom")
            age = st.number_input("Âge", min_value=0, max_value=120, value=21, step=1)
            like_cloud = st.checkbox("J'aime le cloud ☁️", value=True)
            color = st.color_picker("Couleur préférée", "#00A5FF")
        with col2:
            birth = st.date_input("Date de naissance", date(2000, 1, 1))
            when = st.time_input("Heure préférée", dtime(9, 0))
            role = st.selectbox("Rôle", ["Étudiant", "Développeur", "Data Analyst", "Autre"])
            msg = st.text_area("Message", placeholder="Dites-nous quelque chose…")

        submitted = st.form_submit_button("Envoyer")

    if submitted:
        errors = []
        if not name:
            errors.append("Le nom est requis.")
        if age < 18:
            errors.append("Vous devez avoir au moins 18 ans.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.success("Formulaire envoyé ✅")
            st.json({
                "name": name,
                "age": age,
                "like_cloud": like_cloud,
                "color": color,
                "birth": str(birth),
                "when": str(when),
                "role": role,
                "msg": msg,
            })


def render_data_charts():
    st.header("🧮 Données & Graphiques")
    st.caption("Éditez le tableau, tracez un graphe et exportez en CSV.")

    # Data synthétique
    np.random.seed(42)
    df = pd.DataFrame({
        "x": np.arange(0, 50),
        "y": np.cumsum(np.random.randn(50))
    })

    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    st.line_chart(edited, x="x", y="y")

    st.download_button("Exporter le DataFrame (CSV)", edited.to_csv(index=False).encode("utf-8"), file_name="edited_data.csv")


def render_camera():
    st.header("📷 Caméra (Webcam)")
    st.caption("Capturez une image directement depuis le navigateur.")

    img = st.camera_input("Prendre une photo")
    if img is not None:
        st.success("Image capturée !")
        st.image(img, caption="Aperçu de la capture", use_container_width=True)


def render_chat():
    st.header("💬 Espace Chat (local)")
    st.caption("Démo d'interface de chat locale — pas de backend externe.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Salut ! Pose-moi une question ici 😊"}
        ]

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    prompt = st.chat_input("Votre message…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Réponse très simple (écho + longueur)
        reply = f"Vous avez dit : '{prompt}'. Longueur: {len(prompt)} caractères."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)


def render_state_cache():
    st.header("🧠 État & Cache")

    # Session state demo
    st.subheader("Session state")
    if "counter" not in st.session_state:
        st.session_state.counter = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("+1"):
            st.session_state.counter += 1
    with col2:
        if st.button("Reset"):
            st.session_state.counter = 0
    with col3:
        st.metric("Compteur", st.session_state.counter)

    st.write("Contenu complet de `st.session_state` :")
    st.json({k: v for k, v in st.session_state.items() if k != "messages"})

    # Cache demo
    st.subheader("Cache (st.cache_data)")
    nums = st.multiselect("Choisissez des nombres à sommer (cache 2s)", [1, 2, 3, 5, 8, 13, 21], default=[1, 2, 3])
    if st.button("Calculer la somme (lent caché)"):
        with st.spinner("Calcul en cours…"):
            s = fake_slow_sum(nums)
        st.success(f"Somme = {s}")


def render_notify_progress():
    st.header("🔔 Notifications, statut & progression")

    with st.status("Traitement d'exemple en 3 étapes…", expanded=False) as status:
        st.write("Étape 1/3 : préparation…")
        time.sleep(0.5)
        st.write("Étape 2/3 : traitement…")
        time.sleep(0.5)
        st.write("Étape 3/3 : finalisation…")
        time.sleep(0.5)
        status.update(label="Terminé !", state="complete", expanded=False)

    st.toast("Petit toast pour dire bonjour 👋", icon="✅")

    st.subheader("Barre de progression")
    progress = st.progress(0, text="Chargement…")
    for i in range(0, 101, 10):
        time.sleep(0.05)
        progress.progress(i, text=f"{i}%")


# ---------------------------
# Main & routing
# ---------------------------

def main():
    st.set_page_config(page_title="Streamlit Playground", page_icon="🧪", layout="wide")

    with st.sidebar:
        st.title("🧪 Playground")
        st.caption("Testez rapidement les composants Streamlit.")
        page = st.radio(
            "Aller à",
            [
                "Accueil",
                "Upload",
                "Formulaires",
                "Données & Graphiques",
                "Caméra",
                "Chat",
                "État & Cache",
                "Notifications & Progression",
            ],
            index=0,
        )
        st.divider()
        st.write("**Debug**")
        st.checkbox("Activer le mode debug", key="debug")
        st.write("Version Streamlit :", st.__version__)

    # Router
    if page == "Accueil":
        render_home()
    elif page == "Upload":
        render_upload()
    elif page == "Formulaires":
        render_forms()
    elif page == "Données & Graphiques":
        render_data_charts()
    elif page == "Caméra":
        render_camera()
    elif page == "Chat":
        render_chat()
    elif page == "État & Cache":
        render_state_cache()
    elif page == "Notifications & Progression":
        render_notify_progress()

    st.divider()
    st.caption("© 2025 – Démo pédagogique Streamlit. Adaptable à vos besoins.")


if __name__ == "__main__":
    main()
