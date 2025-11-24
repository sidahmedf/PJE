# Nettoyage/main.py

from column_detection.label_column_detector import FinalLabelDetector
from column_detection.tweet_column_detector import FinalTweetDetector, HybridDetector
from export.shipment import ShipmentManager
from file_validation.file_validation import FileValidation
from tweet_cleaning.tweet_cleaner import TweetCleaner

import tempfile
import os
import pandas as pd

def main(file) -> dict:
    """
    Lance le pipeline complet sur un fichier Streamlit (UploadedFile).
    Retourne un dict avec infos et chemins d'export.
    """
    # Écrit le fichier temporairement (car ton code attend un chemin)
    suffix = os.path.splitext(file.name)[1] or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file.getvalue())
    tmp.flush()
    tmp.close()

    csv_path = tmp.name

    # 1️⃣ Validation
    fv = FileValidation(csv_path)
    if not fv.validate():
        raise ValueError("❌ Validation échouée : format ou séparateur invalide")

    # 2️⃣ Lecture CSV
    df = fv.smart_read_csv()

    # 3️⃣ Détection des colonnes
    label_detector = FinalLabelDetector()
    tweet_detector = FinalTweetDetector(fallback_detector=HybridDetector())

    label_idx = label_detector.detect(df)
    tweet_idx = tweet_detector.detect(df)

    if label_idx is None or tweet_idx is None:
        raise ValueError("Impossible de détecter automatiquement les colonnes label/tweet")

    # 4️⃣ Nettoyage
    cleaner = TweetCleaner()
    cleaned_df = cleaner.clean_dataframe(df, tweet_idx=tweet_idx, label_idx=label_idx)

    # 5️⃣ Exports
    outdir = tempfile.mkdtemp(prefix="tweetclean_")
    full_csv = ShipmentManager(mode="csv", output_path=os.path.join(outdir, "final_cleaned_full.csv")).ship(
        cleaned_df, keep_extra=True, label_idx=label_idx, tweet_idx=tweet_idx
    )
    min_csv = ShipmentManager(mode="csv", output_path=os.path.join(outdir, "final_cleaned_min.csv")).ship(
        cleaned_df, keep_extra=False, label_idx=label_idx, tweet_idx=tweet_idx
    )

    return {
        "cleaned_df": cleaned_df,
        "label": df.columns[label_idx],
        "tweet": df.columns[tweet_idx],
        "full_csv": full_csv,
        "min_csv": min_csv,
    }
