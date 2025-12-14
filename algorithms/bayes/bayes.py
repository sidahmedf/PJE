import csv
import math
from collections import defaultdict
import os

# Codes standards
CLASS_LABELS = {
    0: "negatif",
    2: "neutre",
    4: "positif"
}


class NaiveBayesClassifier:
    """
    Adaptation Orientée Objet de ton script fonctionnel.
    S'intègre parfaitement dans le wrapper du projet.
    """

    def __init__(self, smoothing=1.0):
        self.smoothing = smoothing
        self.prior = {}
        self.cond_prob = {}
        self.vocab = set()
        self.classes = set()

    def _tokenize(self, text):
        """Tokenisation simple : minuscule + split"""
        if not isinstance(text, str):
            return []
        return text.lower().split()

    def fit(self, data):
        """
        Entraîne le modèle.

        IMPORTANT : Pour être compatible avec ton Wrapper ET ton script perso,
        cette méthode détecte automatiquement l'ordre (Label, Tweet) ou (Tweet, Label).
        """
        self.classes = set()
        self.vocab = set()

        clean_data = []

        # 1. Normalisation des données & Détection du format
        if not data:
            return

        # On regarde le premier élément pour savoir qui est le Label (int)
        first_a, first_b = data[0]

        is_label_first = isinstance(first_a, int) or (isinstance(first_a, float) and first_a.is_integer())

        for item in data:
            if is_label_first:
                label, tweet = int(item[0]), str(item[1])
            else:
                tweet, label = str(item[0]), int(item[1])

            # On ne garde que les labels valides pour éviter le bug du -1
            if label in [0, 2, 4]:
                clean_data.append((label, tweet))
                self.classes.add(label)

        # 2. Initialisation des compteurs
        word_count = {c: defaultdict(int) for c in self.classes}
        total_words = {c: 0 for c in self.classes}
        class_count = defaultdict(int)

        # 3. Comptage (Logique de ton script)
        for label, tweet in clean_data:
            class_count[label] += 1
            words = self._tokenize(tweet)
            for w in words:
                self.vocab.add(w)
                word_count[label][w] += 1
                total_words[label] += 1

        # 4. Calcul des probabilités
        N = len(self.vocab)
        total_tweets = len(clean_data)

        # P(c)
        self.prior = {c: class_count[c] / total_tweets for c in self.classes}

        # P(m|c) avec lissage (Ton calcul exact)
        self.cond_prob = {}
        for c in self.classes:
            self.cond_prob[c] = {}
            # Dénominateur pré-calculé pour la boucle
            denom = total_words[c] + (self.smoothing * N)

            for w in self.vocab:
                # Formule : (count + alpha) / (total + alpha*V)
                self.cond_prob[c][w] = (word_count[c][w] + self.smoothing) / denom

        print(f"✅ Modèle entraîné sur {len(clean_data)} tweets valides.")

    def predict_one(self, text):
        """Classification d'un tweet (Logique de ton script)"""
        if not self.prior:
            return 2  # Neutre par défaut si pas entraîné

        words = self._tokenize(text)
        scores = {}

        for c in self.prior:
            # log(Prior)
            score = math.log(self.prior[c])

            for w in words:
                if w in self.vocab:
                    # + log(Probabilité Conditionnelle)
                    score += math.log(self.cond_prob[c][w])

            scores[c] = score

        # Retourne la classe avec le score max
        return max(scores, key=scores.get)

    def predict_batch(self, texts):
        return [self.predict_one(t) for t in texts]


# =========================================================
#  PARTIE SCRIPT (Pour que tu puisses tester comme avant)
# =========================================================

def load_training_csv_legacy(path):
    """Ton ancien chargeur de CSV"""
    data = []
    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Sauter header
            for row in reader:
                if row and len(row) >= 2:
                    try:
                        # Ton format : int(row[0]) = label
                        data.append((int(row[0]), row[1]))
                    except:
                        continue
    except FileNotFoundError:
        print("Fichier introuvable.")
    return data


def load_test_csv_legacy(path):
    rows = []
    header = None
    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row: rows.append(row)
    except:
        pass
    return rows, header


def save_predictions_legacy(path, rows, header, predictions):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            new_header = (header + ["pred_num", "pred_txt"]) if header else ["pred_num", "pred_txt"]
            writer.writerow(new_header)
            for row, pred in zip(rows, predictions):
                writer.writerow(row + [pred, CLASS_LABELS.get(pred, "?")])
        print(f"Sauvegardé : {path}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("--- 🎲 Naive Bayes (Mode Standalone) ---")

    # On cherche le fichier test.csv à la racine du projet
    # (On remonte de 2 dossiers car on est dans algorithms/bayes/)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    csv_path = os.path.join(base_dir, "test.csv")

    # 1. Chargement
    print(f"Chargement de {csv_path}...")
    training_data = load_training_csv_legacy(csv_path)

    if training_data:
        # 2. Entraînement via la Classe
        nb = NaiveBayesClassifier(smoothing=1.0)
        nb.fit(training_data)  # La classe gère le format (Label, Tweet)

        # 3. Test sur un exemple
        ex = "I love this app"
        res = nb.predict_one(ex)
        print(f"\nTest '{ex}' -> {res} ({CLASS_LABELS.get(res)})")

        # 4. Test sur le fichier complet (comme ton script)
        rows, header = load_test_csv_legacy(csv_path)
        if rows:
            tweets = [r[1] for r in rows if len(r) > 1]  # On suppose tweet en col 1
            preds = nb.predict_batch(tweets)

            out = os.path.join(base_dir, "result", "bayes_legacy_result.csv")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            save_predictions_legacy(out, rows, header, preds)