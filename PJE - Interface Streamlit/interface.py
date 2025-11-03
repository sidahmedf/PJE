# streamlit_app.py
"""
Interface de démo Streamlit pour tester rapidement les fonctionnalités clés :
- Upload de fichiers (images, CSV/Excel, texte, PDF, autres)
- Éditeur de données + graphiques


▶️ Lancer :
    pip install streamlit pandas numpy
    streamlit run streamlit_app.py
"""

from __future__ import annotations

# --- Charger /Users/.../PJE - Nettoyage/main.py par chemin absolu
import importlib.util
import time
from typing import List
import sys
import numpy as np
import pandas as pd
import streamlit as st

MAIN_PATH = "/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Nettoyage/main.py"

# 🔧 Ajouter le dossier "PJE - Nettoyage" au PYTHONPATH
sys.path.append("/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Nettoyage")

@st.cache_resource(show_spinner=False)
def load_cleaning_module():
    spec = importlib.util.spec_from_file_location("tweet_clean_main", MAIN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

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
        - 📤 *Upload* : importez plusieurs fichiers à la fois et prévisualisez-les une fois nettoyés.
        - 🧮 *Données & Graphiques* : Tracez un graphe pour voir la précision de notre tri.
        """
    )

    with st.expander("Pour faciliter le tri de vos données…"):
       st.write(
              """
                1. Utilisez la section *Upload* pour importer vos fichiers.
                2. Nettoyez et éditez vos données dans *Données & Graphiques*.
                3. Exportez vos données nettoyées via le bouton de téléchargement.
                """
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

    if files:
        st.divider()
        st.subheader("🧹 Lancer le nettoyage avec ton pipeline")

        if st.button("Nettoyer tous les CSV avec Nettoyage/main(files)"):
            mod = load_cleaning_module()
            for f in files:
                # On ne traite que CSV/Excel ici (à toi d'élargir si besoin)
                if not (f.name.lower().endswith(".csv") or f.name.lower().endswith((".xls", ".xlsx"))):
                    st.info(f"⏭️ {f.name} ignoré (pas un CSV/Excel).")
                    continue

                with st.status(f"Nettoyage en cours : {f.name}", expanded=False) as status:
                    try:
                        result = mod.main(f)  # <-- TON main(file) dans /PJE - Nettoyage/main.py
                        # result attendu: dict avec cleaned_df, label, tweet, full_csv, min_csv
                        st.success(f"✅ {f.name} — label: {result['label']} | tweet: {result['tweet']}")

                        with st.expander(f"👀 Aperçu {f.name} (5 premières lignes)"):
                            st.dataframe(result["cleaned_df"].head(5), use_container_width=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            with open(result["min_csv"], "rb") as fh:
                                st.download_button(
                                    "⬇️ Minimal (label+tweet)",
                                    fh.read(),
                                    file_name="cleaned_min.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        with c2:
                            with open(result["full_csv"], "rb") as fh:
                                st.download_button(
                                    "⬇️ Complet (toutes colonnes)",
                                    fh.read(),
                                    file_name="cleaned_full.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        status.update(label="✅ Terminé", state="complete")
                    except Exception as e:
                        status.update(label="❌ Échec", state="error")
                        st.error(f"Erreur sur {f.name} : {e}")


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



# ---------------------------
# Main & routing
# ---------------------------

def main():
    st.set_page_config(page_title="Streamlit Playground", page_icon="🧪", layout="wide")

    with st.sidebar:
        st.title("Interface graphique")
        st.caption("Nettoyage de données avec Streamlit")
        page = st.radio(
            "Aller à",
            [
                "Accueil",
                "Upload",
                "Données & Graphiques",
            ],
            index=0,
        )


    # Router
    if page == "Accueil":
        render_home()
    elif page == "Upload":
        render_upload()

    elif page == "Données & Graphiques":
        render_data_charts()

    st.divider()
    st.caption("© 2025 – Démo pédagogique Streamlit. Adaptable à vos besoins.")


if __name__ == "__main__":
    main()
