# Nettoyage/main.py

from column_detection.label_column_detector import FinalLabelDetector
from column_detection.tweet_column_detector import FinalTweetDetector, HybridDetector
from export.shipment import ShipmentManager
from file_validation.file_validation import FileValidation
from column_detection.label_column_detector  import FinalLabelDetector, LengthBasedDetector
from column_detection.tweet_column_detector  import FinalTweetDetector, HybridDetector
from tweet_cleaning.tweet_cleaner import TweetCleaner
from export.shipment import ShipmentManager

# ===============================================================
#  1️⃣ Load & Validate Input File
# ===============================================================

csv_path = "testdata.manual.2009.06.14.csv"


print("🔍 Step 1: Validating input file...\n")
fv = FileValidation(csv_path)
if not fv.validate():
    print("❌ File validation failed. Please check the CSV and retry.")
    exit()
print("✅ File validated successfully.\n")

# ===============================================================
#  2️⃣ Load CSV
# ===============================================================

print("📂 Step 2: Loading CSV...\n")

try:
    df = fv.smart_read_csv()   # use FileValidation's smart reader
    print(f"✅ Loaded CSV '{csv_path}' successfully! Shape: {df.shape}")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    exit()
# ===============================================================
#  3️⃣ Detect Columns
# ===============================================================

print("\n🧠 Step 2: Detecting key columns...")

label_detector = FinalLabelDetector()
tweet_detector = LengthBasedDetector()

label_idx = label_detector.detect(df)
tweet_idx = tweet_detector.detect(df)

if label_idx is None or tweet_idx is None:
    print("❌ Could not detect label/tweet columns automatically.")
    exit()
print(f"✅ Detected label column: index {label_idx} ({df.columns[label_idx]})")
print(f"✅ Detected tweet column: index {tweet_idx} ({df.columns[tweet_idx]})")
"""

# ===============================================================
#  3️⃣ SELECT COLUMNS MANUALLY
# ===============================================================

print("\n🧠 Step 2: Selecting columns manually...")

label_idx = 0         # Pas de colonne label
tweet_idx = 5            # La première colonne est le tweet

print(f"👉 Using tweet column index = {tweet_idx}")
print("👉 No label column (classification à faire ensuite).")
"""
# ===============================================================
#  4️⃣ Clean Tweets
# ===============================================================

print("\n🧹 Step 3: Cleaning dataset...\n")

print(df.head(3))
print("Raw first tweet:", df.iloc[0, tweet_idx])

cleaner = TweetCleaner()
cleaned_df = cleaner.clean_dataframe(df, tweet_idx=tweet_idx, label_idx=label_idx)

# ===============================================================
#  5️⃣ Export Results
# ===============================================================

print("\n🚚 Step 4: Exporting cleaned results...")

# --- Full CSV (all columns)
csv_full_path = ShipmentManager(
    mode="csv", output_path="output/final_cleaned_full.csv"
).ship(
    cleaned_df,
    keep_extra=True,
    label_idx=label_idx,
    tweet_idx=tweet_idx
)

# --- Minimal CSV (label + tweet only)
csv_min_path = ShipmentManager(
    mode="csv", output_path="output/final_cleaned_min.csv"
).ship(
    cleaned_df,
    keep_extra=False,
    label_idx=label_idx,
    tweet_idx=tweet_idx
)

print(f"\n✅ Exports completed:")
print(f"   • Full CSV → {csv_full_path}")
print(f"   • Minimal CSV (label+tweet) → {csv_min_path}")


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
