# Guide Développeur : Comment ajouter un nouvel Algorithme

Ce projet est organisé autour d’une **interface Streamlit** avec plusieurs onglets (Data, Annotation, Keywords, KNN, Clustering, Bayes, Comparison).
Avant de modifier ou d’ajouter un algorithme, il est utile de **voir l’application en action** pour comprendre où vos changements apparaîtront.

---

## 👀 Lancer l’App & Comprendre la GUI

### 1. Démarrer l’application

Depuis la racine du projet (là où se trouve `main.py`), lancer :

```bash
streamlit run main.py
```

Cela va :

- Configurer la page globale (titre, layout, sidebar…).  
- Appeler une fonction centrale (ex: `run_app()`) située dans `gui/layout.py`.  
- Afficher les **7 onglets principaux** dans l’interface.

### 2. Structure de la GUI (où vont les modifications)

- `gui/layout.py`  
  - Contient la fonction principale (ex: `run_app()`) qui :
    - Crée les onglets (`st.tabs([...])`)
    - Route chaque onglet vers son module (`gui/tabs/...`)
    - Passe le `manager` aux différentes vues

- `gui/tabs/`  
  - Chaque fichier représente un onglet spécifique :
    - `data_cleaning.py` → Onglet **1. Data & Cleaning**
    - `annotation.py` → Onglet **2. Annotation**
    - `keywords.py` → Onglet **3. Keywords**
    - `knn.py` → Onglet **4. KNN**
    - `clustering.py` → Onglet **5. Clustering**
    - `bayes.py` → Onglet **6. Bayes**
    - `comparison.py` → Onglet **7. Comparison**
  - Chaque module expose une fonction du type `render(manager)` qui :
    - Affiche le contenu Streamlit de l’onglet (titres, sliders, boutons, etc.)
    - Utilise `manager` pour appeler les wrappers d’algorithmes

> 💡 **En résumé :**
> - Les **algorithmes** sont définis dans `algorithms/` et exposés via des **wrappers** dans `core/`.
> - Les **onglets Streamlit** dans `gui/tabs/` ne contiennent que de l’UI et appellent ces wrappers.
> - Pour « voir » vos modifications : relancer `streamlit run main.py` et jouer avec l’onglet correspondant.

---

## 🔢 Pipeline Algorithme en 4 Étapes

Si vous voulez procéder au développement d'un nouveau module (ex: **Clustering** ou **Bayes**), suivez exactement ce pipeline.

---

## Étape 1 : Écrire les Maths 🧮

Créez votre logique dans le dossier `algorithms/`.  
⚠️ **N'importez jamais Streamlit ici.**

### Exemple
Créer :
```text
algorithms/clustering/hierarchical.py
```

Écrire des fonctions qui prennent des données brutes et retournent des résultats
(clusters, matrice, dendrogramme, etc.).

---

## Étape 2 : Créer le Wrapper 🎁

Aller dans `core/wrappers.py`.  
Créer une classe qui hérite de `BaseAlgorithm`.  
Elle sert d'« enveloppe » pour que l'application comprenne votre code.

### Exemple (schéma simplifié)
```python
# core/wrappers.py
from algorithms.clustering.hierarchical import ma_fonction_clustering

class ClusteringWrapper(BaseAlgorithm):
    name = "Hierarchical Clustering"
    
    def fit(self, data):
        # Appelez votre fonction Python pure de l’Étape 1
        self.result = ma_fonction_clustering(data)
```

---

## Étape 3 : Enregistrer l'Algorithme 📝

Aller dans `core/manager.py`.  
Importer votre nouveau wrapper et l’ajouter au manager.

### Exemple
```python
# core/manager.py
from .wrappers import ClusteringWrapper

manager = AlgorithmManager([
    ("KNN", KNNWrapper()),
    ("Clustering", ClusteringWrapper()),  # <--- Ajoutez cette ligne
])
```

---

## Étape 4 : Construire l'Interface 🎨

Aller dans le fichier correspondant dans `gui/tabs/`.

Exemple : modifier :
```text
gui/tabs/clustering.py
```

Dans ce fichier :

- Utiliser `manager.get_current()` ou directement `manager` pour accéder à votre wrapper.
- Utiliser `st.slider`, `st.button`, etc., pour contrôler les paramètres et lancer le modèle.
- Afficher résultats, métriques, visualisations, etc.

---

## ✅ Liste des Tâches & Statut

| Module                | Statut      | Assigné à |
|-----------------------|-------------|-----------|
| 1. Data & Cleaning    | 🚧 En Cours |           |
| 2. Annotation Studio  | 🚧 En Cours |           |
| 3. Keywords Algo      | 🚧 En Cours  |           |
| 4. KNN Algo           | 🚧 En Cours  |           |
| 5. Clustering Algo    | 📝 À faire  |           |
| 6. Naive Bayes Algo   | 📝 À faire  |           |
| 7. Comparison         | 📝 À faire  |           |

---

## ⚠️ Règles Importantes

- Ne jamais écrire de logique d’algorithme dans `gui/`
- Ne jamais mettre de widgets Streamlit dans `algorithms/` ou `core/`
- Toujours lancer l’application via `main.py` avec :  
  ```bash
  streamlit run main.py
  ```
