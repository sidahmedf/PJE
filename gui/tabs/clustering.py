import streamlit as st
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import pandas as pd
import numpy as np
from sklearn.metrics import adjusted_rand_score


def render(manager):
    st.header("🧶 Clustering Hiérarchique (TP)")
    st.markdown(
        "Implémentation des pipelines du cours : **Average/Complete** (Distance Mots Communs) et **Ward** (TF-IDF).")

    # 1. Chargement & Échantillonnage
    if 'train_df' not in st.session_state:
        st.warning("⚠️ Veuillez d'abord charger les données dans l'onglet '1. Data & Cleaning'.")
        return

    df = st.session_state['train_df']
    col_text_idx = st.session_state.get('cleaned_text_col_idx', 1)
    col_label_idx = st.session_state.get('cleaned_label_col_idx', 0)

    # Slider pour limiter la taille (car matrice N*N est lourde)
    n_samples = st.slider("Taille de l'échantillon (Tweets)", 50, 300, 100, help="Réduisez si c'est trop lent.")
    df_sample = df.iloc[:n_samples].copy()

    # Préparation des données
    data_train = []
    labels_reels = []
    for i in range(len(df_sample)):
        txt = str(df_sample.iloc[i, col_text_idx])
        # Gestion safe du label (si non supervisé, on met 0)
        lbl = int(df_sample.iloc[i, col_label_idx]) if col_label_idx is not None else 0
        data_train.append((lbl, txt))
        labels_reels.append(lbl)

    st.info(f"Analyse sur **{len(data_train)}** tweets.")

    # 2. Configuration
    st.subheader("Paramètres")
    c1, c2 = st.columns(2)
    with c1:
        k_clusters = st.slider("Nombre de clusters (K)", 2, 6, 3)
    with c2:
        method = st.selectbox("Méthode de lien", ["ward", "average", "complete"])
        if method == "ward":
            st.caption("✅ **Bonus**: Utilise TF-IDF + Distance Euclidienne.")
        else:
            st.caption("✅ **Standard**: Utilise Distance 'Mots Communs' (Jaccard).")

    # --- Initialisation de l'algo (HORS du bouton pour persistance) ---
    manager.select("Clustering")
    algo = manager.get_current()

    # 3. Lancer l'algorithme
    if st.button("🚀 Lancer le Clustering", type="primary"):
        with st.spinner("Calcul des distances et construction du dendrogramme..."):
            algo.set_params(n_clusters=k_clusters, linkage=method)
            algo.fit(data_train)

            # Sauvegarde dans la session
            st.session_state['clustering_trained'] = True
            st.session_state['clustering_linkage'] = algo.get_linkage_matrix()
            st.session_state['clustering_labels'] = algo.get_labels()

        st.success("Terminé !")

    # --- Affichage des résultats ---
    if st.session_state.get('clustering_trained'):

        # A. Dendrogramme
        st.subheader("Visualisation : Dendrogramme")
        Z = st.session_state.get('clustering_linkage')

        if Z is not None:
            fig, ax = plt.subplots(figsize=(10, 5))
            dendrogram(Z, ax=ax, truncate_mode='lastp', p=k_clusters + 15, show_leaf_counts=True)
            plt.title(f"Dendrogramme ({method})")
            plt.xlabel("Index des Tweets / Clusters")
            plt.ylabel("Distance")
            st.pyplot(fig)

        # B. Évaluation
        st.subheader("Évaluation")
        if col_label_idx is None:
            st.warning("Impossible d'évaluer : pas de colonne Label réelle sélectionnée.")
        else:
            labels_predits = st.session_state.get('clustering_labels')

            # ARI
            ari = adjusted_rand_score(labels_reels, labels_predits)

            # Matrice de Confusion (via Pandas Crosstab)
            df_cm = pd.crosstab(
                pd.Series(labels_reels, name="Label Réel"),
                pd.Series(labels_predits, name="Cluster Prédiction")
            )

            col_met1, col_met2 = st.columns([1, 2])
            with col_met1:
                st.metric("Adjusted Rand Index (ARI)", f"{ari:.4f}")
            with col_met2:
                st.write("**Matrice de Confusion**")
                st.dataframe(df_cm, use_container_width=True)

        # C. Test Interactif
        st.divider()
        st.subheader("Test Manuel")
        user_input = st.text_input("Tapez un tweet pour voir à quel cluster il appartiendrait :")

        if user_input:
            cluster_id = algo.predict_one(user_input)
            st.info(f"Ce tweet serait classé dans le **Cluster {cluster_id}**")