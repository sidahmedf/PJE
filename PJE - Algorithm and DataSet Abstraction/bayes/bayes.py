import csv
import math
from collections import defaultdict

# On garde les codes 0 / 2 / 4 comme dans ton fichier
CLASS_LABELS = {
    0: "negatif",
    2: "neutre",
    4: "positif"
}


# ------------------------
# 1. Tokenisation simple
# ------------------------
def tokenize(text):
    return text.lower().split()


# ------------------------
# 2. Chargement du fichier d'apprentissage (test.csv)
#    Format : label,tweet
# ------------------------
def load_training_csv(path):
    data = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # ← SAUTER L'EN-TÊTE
        for row in reader:
            if not row:
                continue
            label = int(row[0])
            tweet = row[1]
            data.append((tweet, label))
    return data



# ------------------------
# 3. Entraînement Naive Bayes
# ------------------------
def train_naive_bayes(data):
    classes = set(label for _, label in data)

    vocab = set()
    word_count = {c: defaultdict(int) for c in classes}
    total_words = {c: 0 for c in classes}
    class_count = defaultdict(int)

    # Comptage
    for tweet, label in data:
        class_count[label] += 1
        words = tokenize(tweet)
        for w in words:
            vocab.add(w)
            word_count[label][w] += 1
            total_words[label] += 1

    N = len(vocab)

    # P(c)
    total_tweets = len(data)
    prior = {c: class_count[c] / total_tweets for c in classes}

    # P(m|c) avec lissage de Laplace
    cond_prob = {}
    for c in classes:
        cond_prob[c] = {}
        for w in vocab:
            cond_prob[c][w] = (word_count[c][w] + 1) / (total_words[c] + N)

    return prior, cond_prob, vocab


# ------------------------
# 4. Classification d'un tweet
# ------------------------
def classify(tweet, prior, cond_prob, vocab):
    words = tokenize(tweet)
    scores = {}

    for c in prior:
        score = math.log(prior[c])
        for w in words:
            if w in vocab:
                score += math.log(cond_prob[c][w])
        scores[c] = score

    # DEBUG : afficher pour les 3 premiers tweets
    if not hasattr(classify, 'count'):
        classify.count = 0

    if classify.count < 3:
        for c in sorted(scores.keys()):
            pass
        classify.count += 1

    return max(scores, key=scores.get)


# ------------------------
# 5. Chargement du fichier à tester
#    Format supposé : une colonne = le tweet
# ------------------------
def load_test_csv(path):
    """Charge le CSV complet en gardant toutes les colonnes"""
    rows = []
    header = None
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Récupérer l'en-tête
        for row in reader:
            if not row:
                continue
            rows.append(row)  # Garder la ligne complète
    return rows, header





# ------------------------
# 6. Sauvegarde du fichier annoté
def save_predictions(path, original_rows, original_header, labels_num):
    """Écrit le CSV en gardant les colonnes d'origine et en ajoutant les prédictions"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Ajoute les nouvelles colonnes à l'en-tête
        new_header = original_header + ["prediction_num", "prediction_texte"] if original_header else ["prediction_num",
                                                                                                       "prediction_texte"]
        writer.writerow(new_header)

        for row, label in zip(original_rows, labels_num):
            new_row = row + [label, CLASS_LABELS.get(label, "inconnu")]
            writer.writerow(new_row)


# ------------------------
# 7. MAIN
# ------------------------
if __name__ == "__main__":
    training_data = load_training_csv("test.csv")

    # DEBUG : Afficher les 5 premiers exemples
    print("📊 Premiers exemples d'entraînement :")
    for i, (tweet, label) in enumerate(training_data[:5]):

        prior, cond_prob, vocab = train_naive_bayes(training_data)

    # 2) Chargement du fichier complet
    rows, header = load_test_csv("final_cleaned_min.csv")

    # 3) DÉTERMINER quelle colonne contient le texte
    # Ajoutez ce debug pour vérifier :

    # Si le texte est en colonne 1 (index 1) :
    tweets_a_tester = [row[1] for row in rows]

    # 4) Prédictions
    predictions = [
        classify(t, prior, cond_prob, vocab)
        for t in tweets_a_tester
    ]

    # 5) Sauvegarde
    save_predictions("result/tweets_annotes.csv", rows, header, predictions)

