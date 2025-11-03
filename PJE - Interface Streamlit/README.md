# 🧪 Interface Streamlit — Prototype d’analyse des fichiers

## 🎯 Objectif du projet

Ce projet vise à créer une **interface web simple avec Streamlit** permettant de :

1. **Importer des fichiers** depuis la page web
2. **Afficher leur contenu** après traitement par notre **algorithme interne**
3. **Calculer et visualiser la précision** sous forme de graphique et tableau interactif

L’idée est de fournir à l’équipe un outil de démonstration rapide, utile pour tester notre pipeline de données et suivre les performances.

---

## ⚙️ Fonctionnalités prévues

### 📤 Import de fichiers

* Upload de plusieurs fichiers (CSV, images, etc.) directement depuis l’interface.
* Vérification du type et affichage automatique du contenu :

  * `CSV / XLSX` → aperçu sous forme de tableau
  * `Images` → affichage direct dans la page
  * `Autres` → téléchargement brut possible

> 💡 Possibilité d’augmenter la limite d’upload via `.streamlit/config.toml` :
>
> ```toml
> [server]
> maxUploadSize = 1000
> ```

---

### 🧮 Passage dans l’algorithme

* Une fois le fichier importé, il est envoyé à **notre algorithme de traitement** (à intégrer dans `analyze_file(file)`).
* L’algo renverra :

  * Un dataframe des résultats
  * Des métriques globales (ex : précision, recall, F1-score, etc.)

---

### 📊 Visualisation des résultats

* Les résultats sont affichés dans un **tableau éditable** (`st.data_editor`)
* Un bouton « Afficher la précision » permet :

  * d’afficher la **métrique de précision**
  * de générer un **graphique dynamique** (ex: `st.line_chart` ou `st.bar_chart`)
  * d’afficher éventuellement une **courbe de progression** ou une jauge de performance

Exemple d’affichage prévu :

```python
if st.button("Afficher la précision"):
    precision = compute_precision(df)
    st.metric("Précision du modèle", f"{precision:.2f} %")
    st.line_chart(df, x="epoch", y="accuracy")
```

---

### 🧠 Évolutions possibles

* Ajouter un **historique** des analyses (fichiers traités + précision)
* Intégrer un **système de connexion (auth simple)** pour les membres de l’équipe
* Possibilité d’exporter les résultats au format CSV / PDF
* Intégration future avec le backend du projet (FastAPI ou Flask)

---

## 🚀 Lancement du projet

1. Installer les dépendances :

   ```bash
   pip install streamlit pandas numpy
   ```

2. Lancer l’application :

   ```bash
   streamlit run interface.py
   ```

3. Ouvrir le navigateur à l’adresse :

   ```
   http://localhost:8501
   ```

---

## 👥 Collaboration

Ce README sert de base commune pour la suite du développement.
👉 **Mathis** : focus sur l’intégration de l’algorithme et des métriques
👉 **Victor** : focus sur l’interface (upload, affichage, graphique, état Streamlit)

---

## 📁 Structure du projet

```
📦 PJE_Sid_Ahmed
 ┣ 📜 interface.py              # Interface principale Streamlit
 ┣ 📁 .streamlit/
 ┃ ┗ 📜 config.toml             # Configuration (limite upload, port, etc.)
 ┣ 📜 README.md                 # Ce document
 ┗ 📁 data/                     # (Optionnel) Fichiers d’entrée/sortie
```

---

## 💬 Notes

* L’interface s’inspire du *playground Streamlit* pour tester toutes les fonctionnalités rapidement.
* Une fois la logique d’analyse intégrée, on pourra créer une **section dédiée aux performances** (graphiques + logs d’exécution).
* Le but est d’avoir un **outil de test rapide** pour valider la cohérence entre les résultats de l’algo et les fichiers d’entrée.

---
