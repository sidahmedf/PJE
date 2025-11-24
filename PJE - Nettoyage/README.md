# 🧼 Pipeline de Nettoyage de Tweets 

Ce dépôt fournit un pipeline **modulaire** pour :
- valider un CSV (avec ou sans en-tête, texte avec ou sans guillemets),
- détecter automatiquement les colonnes **label** et **tweet**,
- nettoyer le texte (URLs, @mentions, hashtags, ponctuation, espaces, etc.),
- filtrer les doublons et ne garder que la **langue dominante**,
- exporter deux CSV :  
  1) **complet** (toutes colonnes)  
  2) **minimal** (*label + tweet nettoyé*).

---


## 🧩 Description des modules

### `file_validation.py`
- Vérifie la validité du fichier CSV (existence, encodage, colonnes, texte).
- Charge les fichiers même **sans en-tête** ou **avec des guillemets**.
- Gère automatiquement les encodages et saute les lignes corrompues.
- Fournit la méthode `smart_read_csv()` : lecture robuste et tolérante.

### `label_detector.py`
- Trouve automatiquement la **colonne de labels (cible)** à partir :
  - du nom d’en-tête (`label`, `target`, `sentiment`, ...),
  - des valeurs (0/1/2, positive/negative, etc.),
  - d’heuristiques (peu de valeurs uniques).

### `tweet_detector.py`
- Détecte la **colonne de texte (tweet)** selon :
  - les noms (`text`, `tweet`, `message`, ...),
  - la longueur moyenne,
  - la densité d’espaces,
  - la variété des textes.

### `rules.py`
- Contient toutes les **règles de nettoyage textuel** :  
  ```
  python
  ToLowercase()
  RemoveURLs()
  RemoveMentions()
  RemoveHashtags()
  RemoveRetweetMarker()
  RemovePunctuation()
  NormalizeWhitespace()
  ```
- Ces règles sont combinées dans `default_rules()`.

### `tweet_cleaner.py`
- Applique les **règles de texte**, puis les **filtres globaux** :
  - Suppression des doublons,
  - Suppression des tweets dans d'autres langues,
  - Suppression des lignes avec des emojis contradictoires.
- Renvoie un **DataFrame nettoyé** prêt à être exporté.

### `shipment.py`
- Gère la **sortie** des données nettoyées :
  ```
  python
  ShipmentManager(mode="csv").ship(df)
  ShipmentManager(mode="json").ship(df)
  ShipmentManager(mode="dataframe").ship(df)
  ```
- Assure que le CSV minimal contient **label + tweet uniquement**.

### `main.py`
- Orchestration complète :
  1. Validation du CSV  
  2. Chargement avec `smart_read_csv()`  
  3. Détection auto des colonnes  
  4. Nettoyage du texte  
  5. Export des résultats

---

## ▶️ Exécution rapide

### Prérequis
```bash
pip install csv pandas langdetect charset-normalizer
```

### Lancer le script
```bash
python main.py
```

Le script :
- lit `data/raw/testdata.manual.2009.06.14.csv`
- nettoie les tweets,
- génère :  
  - `data/exports/final_cleaned_full.csv` (toutes colonnes)  
  - `data/exports/final_cleaned_min.csv` (label + tweet)

---

## 🧠 Utilisation du pipeline dans une autre app (GUI, etc.)

### Exemple simple (6 étapes)
```python
from file_validation import FileValidation
from column_detection.label_column_detector  import FinalLabelDetector
from column_detection.tweet_column_detector  import FinalTweetDetector, HybridDetector
from tweet_cleaning.tweet_cleaner import TweetCleaner
from export.shipment import  ShipmentManager

# 1️⃣ Charger le CSV
fv = FileValidation("data/raw/mytweets.csv")
assert fv.validate(), "CSV invalide"
df = fv.smart_read_csv()

# 2️⃣ Détecter les colonnes
label_idx = FinalLabelDetector().detect(df)
tweet_idx = FinalTweetDetector(fallback_detector=HybridDetector()).detect(df)

# 3️⃣ Nettoyer
cleaner = TweetCleaner()
cleaned_df = cleaner.clean_dataframe(df, tweet_idx=tweet_idx, label_idx=label_idx)

# 4️⃣ Exporter (Full ou Minimal)
ShipmentManager(mode="csv", output_path="data/exports/full.csv").ship(cleaned_df, keep_extra=True, label_idx=label_idx, tweet_idx=tweet_idx)

ShipmentManager(mode="csv", output_path="data/exports/min.csv").ship(cleaned_df, keep_extra=False, label_idx=label_idx, tweet_idx=tweet_idx)

