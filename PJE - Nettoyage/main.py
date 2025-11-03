# ===============================================================
#  main.py — Full Tweet Cleaning Pipeline (simplified)
# ===============================================================

from file_validation.file_validation import FileValidation
from column_detection.label_column_detector  import FinalLabelDetector
from column_detection.tweet_column_detector  import FinalTweetDetector, HybridDetector
from tweet_cleaning.tweet_cleaner import TweetCleaner
from export.shipment import ShipmentManager

# ===============================================================
#  1️⃣ Load & Validate Input File
# ===============================================================

csv_path = "training.1600000.processed.noemoticon.csv"


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
tweet_detector = FinalTweetDetector(fallback_detector=HybridDetector())

label_idx = label_detector.detect(df)
tweet_idx = tweet_detector.detect(df)

if label_idx is None or tweet_idx is None:
    print("❌ Could not detect label/tweet columns automatically.")
    exit()

print(f"✅ Detected label column: index {label_idx} ({df.columns[label_idx]})")
print(f"✅ Detected tweet column: index {tweet_idx} ({df.columns[tweet_idx]})")

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


