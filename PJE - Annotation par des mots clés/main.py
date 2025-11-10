from annotator import KeywordAnnotator
from evaluate import evaluate_accuracy
import pandas as pd
import os

def main(file):
    """Annote un fichier uploadé via Streamlit."""
    # 1️⃣ Charger le fichier en DataFrame
    if file.name.endswith(".csv"):
        df_input = pd.read_csv(file, encoding="latin-1")
    else:
        df_input = pd.read_excel(file)

    # 2️⃣ Construire le chemin absolu vers keywords.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(current_dir, "keywords.json")

    # 3️⃣ Annoter le dataset
    annotator = KeywordAnnotator(json_path=keywords_path)

    # Sauvegarder temporairement dans le même dossier
    temp_input = os.path.join(current_dir, f"temp_{file.name}")
    df_input.to_csv(temp_input, index=False)

    output_path = os.path.join(current_dir, f"annotated_{file.name}")
    df = annotator.annotate(temp_input, output_path, mode="add")

    # 4️⃣ Retourner les résultats
    return {
        "annotated_df": df,
        "full_csv": output_path
    }
