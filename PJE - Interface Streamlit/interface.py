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
ANNOT_PATH = "/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Annotation par des mots clés/main.py"

# 🔧 Ajouter les dossiers au PYTHONPATH
sys.path.append("/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Nettoyage")
sys.path.append("/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Annotation par des mots clés")

@st.cache_resource(show_spinner=False)
def load_cleaning_module():
    spec = importlib.util.spec_from_file_location("tweet_clean_main", MAIN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


import os


@st.cache_resource(show_spinner=False)
def load_annotation_module():
    annot_dir = "/Users/mathislefevre/Documents/PJE_Sid_Ahmed/PJE - Annotation par des mots clés"

    # Sauvegarder le dossier actuel
    original_cwd = os.getcwd()

    try:
        # Se placer dans le dossier d'annotation avant de charger le module
        os.chdir(annot_dir)

        spec = importlib.util.spec_from_file_location("tweet_annotate_main", ANNOT_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        return mod
    finally:
        # Restaurer le dossier d'origine
        os.chdir(original_cwd)


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
    if st.button("Classifier vos tweets avec Annotation/main(files)"):
        mod = load_annotation_module()
        for f in files:
            if not f.name.lower().endswith((".csv", ".xls", ".xlsx")):
                st.info(f"⏭️ {f.name} ignoré (pas un CSV/Excel).")
                continue

            with st.status(f"Annotation en cours : {f.name}", expanded=False) as status:
                try:
                    result = mod.main(f)  # Appelle le main() du module d'annotation
                    st.success(f"✅ {f.name} annoté")

                    # Affiche les résultats (adapte selon ce que retourne ton main)
                    if isinstance(result, dict) and "annotated_df" in result:
                        with st.expander(f"👀 Aperçu annoté {f.name}"):
                            st.dataframe(result["annotated_df"].head(5), use_container_width=True)

                        # Bouton de téléchargement si un CSV annoté est généré
                        if "full_csv" in result:
                            with open(result["full_csv"], "rb") as fh:
                                st.download_button(
                                    "⬇️ Télécharger le CSV annoté",
                                    fh.read(),
                                    file_name=f"annotated_{f.name}",
                                    mime="text/csv"
                                )
                    status.update(label="✅ Terminé", state="complete")
                except Exception as e:
                    status.update(label="❌ Échec", state="error")
                    st.error(f"Erreur sur {f.name} : {e}")


# python
def render_data_charts():
    import numpy as np
    import pandas as pd

    st.header("🧮 Données & Graphiques — précision liée au CSV uploadé")
    st.caption("Chargez un CSV ou utilisez des données synthétiques, puis choisissez les colonnes de vérité/prédiction.")

    uploaded = st.file_uploader("Charger un fichier CSV (optionnel)", type=["csv"], help="Si vous chargez un CSV, il servira de source de données.")
    df = None
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.success(f"Fichier chargé : {uploaded.name} — {len(df)} lignes")
            st.dataframe(df.head(5), use_container_width=True)
        except Exception as e:
            st.error(f"Impossible de lire le CSV : {e}")

    if df is None:
        np.random.seed(42)
        df = pd.DataFrame({"x": np.arange(0, 50), "y": np.cumsum(np.random.randn(50))})
        st.info("Aucun CSV chargé — données synthétiques utilisées")

    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    cols = list(edited.columns)
    choose_true = st.selectbox("Colonne étiquette vraie (sélectionnez ou créer synthétique)", ["(Créer synthétique)"] + cols, index=0 if "true_label" not in cols else cols.index("true_label") + 1)
    choose_prob = st.selectbox("Colonne probabilité prédite (optionnelle)", ["(Aucune)"] + cols, index=0 if "pred_prob" not in cols else cols.index("pred_prob") + 1)
    choose_pred_label = st.selectbox("Colonne prédiction binaire (optionnelle)", ["(Aucune)"] + cols, index=0 if "pred_label" not in cols else cols.index("pred_label") + 1)

    # Construire true_label
    if choose_true == "(Créer synthétique)":
        true = pd.Series(np.random.choice([0, 1], size=len(edited), p=[0.6, 0.4]), index=edited.index, name="true_label")
    else:
        true = edited[choose_true].astype(int, errors="ignore")
        true = pd.to_numeric(true, errors="coerce").fillna(0).astype(int)

    # Construire prédiction
    pred = None
    if choose_prob != "(Aucune)":
        prob = pd.to_numeric(edited[choose_prob], errors="coerce").clip(0.0, 1.0).fillna(0.0)
    else:
        prob = None

    if prob is None and choose_pred_label != "(Aucune)":
        pred = pd.to_numeric(edited[choose_pred_label], errors="coerce").fillna(0).astype(int)
    elif prob is None:
        # pas de colonne fournie -> créer prob synthétique
        prob = pd.Series(np.clip(0.3 + 0.4 * np.random.randn(len(edited)), 0.0, 1.0), index=edited.index)

    # Si on a une probabilité, proposer un seuil
    if prob is not None:
        threshold = st.slider("Seuil de décision (pred_prob → pred_label)", 0.0, 1.0, 0.5, 0.01)
        pred = (prob >= threshold).astype(int)
    else:
        # si pred est toujours None (cas improbable), créer aléatoire
        if pred is None:
            pred = pd.Series(np.random.choice([0, 1], size=len(edited)), index=edited.index)

    true = true.astype(int)
    pred = pred.astype(int)

    TP = int(((true == 1) & (pred == 1)).sum())
    FP = int(((true == 0) & (pred == 1)).sum())
    FN = int(((true == 1) & (pred == 0)).sum())
    TN = int(((true == 0) & (pred == 0)).sum())

    precision = TP / (TP + FP) if (TP + FP) > 0 else float("nan")

    c1, c2 = st.columns([1, 2])
    with c1:
        if not np.isnan(precision):
            st.metric("Précision", f"{precision:.2%}", delta=None)
        else:
            st.metric("Précision", "N/A", delta=None)
        st.write("Matrice de confusion (comptes)")
        counts = pd.DataFrame({"count": [TP, FP, FN, TN]}, index=["TP", "FP", "FN", "TN"])
        st.table(counts)

    with c2:
        st.subheader("Visualisation des comptes")
        st.bar_chart(counts)

    # Courbe précision vs seuil si prob disponible
    if prob is not None:
        thr_vals = np.linspace(0.0, 1.0, 101)
        prec_vals = []
        for thr in thr_vals:
            p = (prob >= thr).astype(int)
            tp = ((true == 1) & (p == 1)).sum()
            fp = ((true == 0) & (p == 1)).sum()
            prec_vals.append(tp / (tp + fp) if (tp + fp) > 0 else np.nan)
        prec_df = pd.DataFrame({"precision": prec_vals}, index=thr_vals)
        st.subheader("Précision en fonction du seuil")
        st.line_chart(prec_df)

    st.download_button("Exporter le DataFrame édité (CSV)", edited.to_csv(index=False).encode("utf-8"), file_name="edited_data.csv")



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
