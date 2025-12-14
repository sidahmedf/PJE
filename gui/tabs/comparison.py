import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

# Import des classes natives (sans passer par le Manager pour avoir des instances multiples)
from algorithms.bayes.bayes import NaiveBayesClassifier
from algorithms.knn.knn_classifier import KNNClassifier
from algorithms.knn.distance import JaccardDistance
from algorithms.knn.voting import MajorityVote
from algorithms.keywords.annotator import AnnotationParams, annotate_tweet


def render(manager):
    st.header("📊 Analyse Expérimentale & Validation Croisée")
    st.markdown("Comparaison des performances selon le protocole du TP (K-Fold Cross-Validation).")

    # 1. Vérification Données
    if 'train_df' not in st.session_state:
        st.error("Veuillez charger les données (Onglet 1).")
        return

    df = st.session_state['train_df']
    col_text = st.session_state.get('cleaned_text_col_idx', 1)
    col_label = st.session_state.get('cleaned_label_col_idx', 0)

    # Préparation Dataset (Liste de tuples)
    dataset = []
    labels_list = []
    for i in range(len(df)):
        try:
            lbl = int(float(df.iloc[i, col_label]))
            txt = str(df.iloc[i, col_text])
            if lbl in [0, 2, 4]:
                dataset.append((lbl, txt))
                labels_list.append(lbl)
        except:
            continue

    st.info(f"Dataset actif : **{len(dataset)}** tweets.")

    # 2. Configuration de l'Expérience
    st.subheader("1. Configuration")

    k_folds = st.slider("Nombre de plis (k)", 2, 10, 5, help="Standard = 10 (mais plus lent)")

    st.write("**Algorithmes à tester :**")

    # Checkbox pour les 6 variantes de Bayes
    check_b1 = st.checkbox("1. Bayes: Présence, Uni-gramme", value=True)
    check_b2 = st.checkbox("2. Bayes: Présence, Bi-gramme", value=True)
    check_b3 = st.checkbox("3. Bayes: Présence, Uni + Bi", value=True)
    check_b4 = st.checkbox("4. Bayes: Fréquence, Uni-gramme", value=True)
    check_b5 = st.checkbox("5. Bayes: Fréquence, Bi-gramme", value=True)
    check_b6 = st.checkbox("6. Bayes: Fréquence, Uni + Bi", value=True)

    st.markdown("---")
    check_knn = st.checkbox("Comparateur: KNN (k=5, Jaccard)", value=True)
    check_kw = st.checkbox("Comparateur: Mots-clés (Règles)", value=True)

    # 3. Moteur de Validation Croisée
    if st.button("🚀 Lancer la Validation Croisée", type="primary"):
        results = []
        barre = st.progress(0, text="Initialisation...")

        # Création des plis
        skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)
        X = np.array([t for l, t in dataset])
        y = np.array([l for l, t in dataset])

        # Liste des configs actives
        configs = []
        if check_b1: configs.append(("Bayes (Présence, Uni)", NaiveBayesClassifier(use_binary=True, n_gram=1)))
        if check_b2: configs.append(("Bayes (Présence, Bi)", NaiveBayesClassifier(use_binary=True, n_gram=2)))
        if check_b3: configs.append(("Bayes (Présence, Uni+Bi)", NaiveBayesClassifier(use_binary=True, n_gram=3)))
        if check_b4: configs.append(("Bayes (Fréquence, Uni)", NaiveBayesClassifier(use_binary=False, n_gram=1)))
        if check_b5: configs.append(("Bayes (Fréquence, Bi)", NaiveBayesClassifier(use_binary=False, n_gram=2)))
        if check_b6: configs.append(("Bayes (Fréquence, Uni+Bi)", NaiveBayesClassifier(use_binary=False, n_gram=3)))

        if check_knn:
            # On recrée une instance KNN fraîche
            dist = JaccardDistance(use_synonyms=False)  # Simplifié pour la vitesse
            knn = KNNClassifier(k=5, distance=dist, voter=MajorityVote())
            configs.append(("KNN (k=5)", knn))

        # Pour les mots-clés, c'est spécial (pas de fit), on le gère comme un algo statique
        kw_params = None
        if check_kw and 'keyword_model' in st.session_state:
            kw_params = st.session_state['keyword_model']
        elif check_kw:
            st.warning("⚠️ Modèle Mots-clés ignoré (non configuré dans l'onglet 3).")

        total_steps = k_folds * len(configs)
        current_step = 0

        # Dictionnaire pour stocker les scores : { "Algo Name": [score_fold1, score_fold2...] }
        scores_map = {name: [] for name, _ in configs}
        if check_kw and kw_params: scores_map["Mots-clés"] = []

        # BOUCLE DE VALIDATION CROISÉE
        for i, (train_idx, test_idx) in enumerate(skf.split(X, y)):
            # Préparation des données du pli
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Format [(label, text)] pour nos algos
            train_set = list(zip(y_train, X_train))
            test_texts = list(X_test)

            # 1. Tester les Algos Entraînables (Bayes / KNN)
            for algo_name, algo_instance in configs:
                barre.progress(int(current_step / total_steps * 100), text=f"Pli {i + 1}/{k_folds} : {algo_name}")

                # Fit & Predict
                algo_instance.fit(train_set)
                preds = algo_instance.predict_batch(test_texts)

                # Score
                acc = accuracy_score(y_test, preds)
                scores_map[algo_name].append(acc)
                current_step += 1

            # 2. Tester l'Algo Mots-clés (Pas d'entraînement, juste predict)
            if check_kw and kw_params:
                preds_kw = [annotate_tweet(t, kw_params) for t in test_texts]
                acc_kw = accuracy_score(y_test, preds_kw)
                scores_map["Mots-clés"].append(acc_kw)

        barre.empty()
        st.success("Analyse terminée !")

        # 4. Affichage des Résultats (Tableau)
        st.subheader("🏆 Résultats (Moyenne des plis)")

        final_stats = []
        for name, scores in scores_map.items():
            final_stats.append({
                "Algorithme": name,
                "Précision Moyenne": np.mean(scores),
                "Écart-type": np.std(scores),
                "Min": np.min(scores),
                "Max": np.max(scores)
            })

        df_res = pd.DataFrame(final_stats).sort_values(by="Précision Moyenne", ascending=False)

        # Formatage pour l'affichage (pourcentage)
        st.dataframe(
            df_res.style.format({
                "Précision Moyenne": "{:.2%}",
                "Écart-type": "{:.2%}",
                "Min": "{:.2%}",
                "Max": "{:.2%}"
            }),
            use_container_width=True
        )

        # 5. Conclusion automatique
        best_algo = df_res.iloc[0]
        st.markdown(f"""
        ### 💡 Conclusion
        L'algorithme le plus performant sur ce dataset est **{best_algo['Algorithme']}** avec une précision moyenne de **{best_algo['Précision Moyenne']:.2%}**.
        """)