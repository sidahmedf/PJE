import streamlit as st
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix


def render(manager):
    st.header("🎲 Algorithme : Naive Bayes")

    # IMPORTANT : On sélectionne l'algo dès l'affichage pour éviter le bug lors du test manuel
    manager.select("Naive Bayes")

    # 1. Vérification des données
    if 'train_df' not in st.session_state or 'test_df' not in st.session_state:
        st.warning("⚠️ Veuillez d'abord charger un fichier dans l'onglet '1. Data & Cleaning'.")
        return

    train_df = st.session_state['train_df']
    test_df = st.session_state['test_df']

    col_text_idx = st.session_state.get('cleaned_text_col_idx', 1)
    col_label_idx = st.session_state.get('cleaned_label_col_idx', 0)

    # Fonction locale pour nettoyer les labels (garde uniquement 0, 2, 4)
    def preparer_donnees(df):
        donnees = []
        labels = []
        for i in range(len(df)):
            try:
                txt = str(df.iloc[i, col_text_idx])
                val_brute = df.iloc[i, col_label_idx]
                lbl = int(float(val_brute))

                if lbl in [0, 2, 4]:
                    donnees.append((lbl, txt))
                    labels.append(lbl)
            except:
                continue
        return donnees, labels

    train_data, labels_train = preparer_donnees(train_df)
    test_data, labels_test_reels = preparer_donnees(test_df)

    if not train_data:
        st.error("⛔ Aucune donnée valide (0, 2, 4) trouvée. Vérifie les colonnes.")
        return

    # 2. Configuration & Entraînement
    st.subheader("1. Configuration & Entraînement")

    col_conf, col_info = st.columns([1, 1])

    with col_conf:
        lissage = st.slider("Lissage (Alpha)", 0.1, 5.0, 1.0, 0.1, help="Gère les mots inconnus.")

    with col_info:
        st.info(f"📊 Données prêtes : **{len(train_data)}** tweets d'entraînement.")

    if st.button("🧠 Entraîner le modèle", type="primary"):
        with st.spinner("Entraînement probabiliste en cours..."):
            algo = manager.get_current()
            algo.set_params(smoothing=lissage)
            algo.fit(train_data)

            st.session_state['bayes_trained'] = True
            st.success("Modèle entraîné avec succès !")

    # 3. Test & Évaluation
    st.divider()
    st.subheader("2. Test & Évaluation")

    if not st.session_state.get('bayes_trained'):
        st.info("Veuillez entraîner le modèle ci-dessus pour accéder aux tests.")
    else:
        # A. Test Manuel
        col_test, col_res = st.columns([3, 1])
        with col_test:
            phrase_user = st.text_input("Tester une phrase :", placeholder="Ce cours est vraiment super !")

        if phrase_user:
            algo = manager.get_current()
            pred = algo.predict_one(phrase_user)

            map_res = {0: "😡 Négatif", 2: "😐 Neutre", 4: "🥰 Positif"}
            resultat_str = map_res.get(pred, f"Classe {pred}")

            with col_res:
                st.markdown(f"### {resultat_str}")

        # B. Évaluation Globale
        st.markdown("---")
        st.write("📊 **Performance sur le Test Set**")

        if st.button("Lancer l'évaluation complète avec naive bayes"):
            algo = manager.get_current()

            # Barre de progression
            barre = st.progress(0, text="Prédiction en cours...")

            textes_test = [t for _, t in test_data]
            predictions = algo.predict_batch(textes_test)

            barre.progress(100, text="Calcul des métriques...")

            acc = accuracy_score(labels_test_reels, predictions)
            cm = confusion_matrix(labels_test_reels, predictions)

            c_metric, c_mat = st.columns([1, 2])

            with c_metric:
                st.metric("Accuracy", f"{acc * 100:.2f}%")
                st.caption(f"Corrects : {int(acc * len(labels_test_reels))}/{len(labels_test_reels)}")

            with c_mat:
                st.write("**Matrice de Confusion**")
                labels_uniques = sorted(list(set(labels_test_reels + predictions)))
                df_cm = pd.DataFrame(
                    cm,
                    index=[f"Vrai {l}" for l in labels_uniques],
                    columns=[f"Pred {l}" for l in labels_uniques]
                )
                st.dataframe(df_cm, use_container_width=True)