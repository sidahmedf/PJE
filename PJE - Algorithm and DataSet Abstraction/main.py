from algorithm_manager import manager
import csv, random, json, os


# ==============================
# AUTO-CREATE ALL JSON FILES
# ==============================
def create_demo_files():
    os.makedirs("tmp", exist_ok=True)

    synonyms_A = {
        "0": ["love", "adore", "enjoy"],
        "1": ["hate", "dislike", "detest"],
        "2": ["kindle", "ereader", "ebook"]
    }

    synonyms_B = {
        "0": ["love", "luv", "loving"],
        "1": ["hate", "h8", "hatred"],
        "2": ["amazon", "kindle", "device"]
    }

    keywords_A = {
        "positive": ["love", "great", "awesome", "happy", "enjoy"],
        "negative": ["hate", "bad", "terrible", "angry", "sad"]
    }

    keywords_B = {
        "positive": ["kindle", "nice", "good", "fun"],
        "negative": ["broken", "slow", "trash", "delay"]
    }

    with open("tmp/syn_A.json", "w") as f: json.dump(synonyms_A, f)
    with open("tmp/syn_B.json", "w") as f: json.dump(synonyms_B, f)
    with open("tmp/key_A.json", "w") as f: json.dump(keywords_A, f)
    with open("tmp/key_B.json", "w") as f: json.dump(keywords_B, f)

    return {
        "synA": "tmp/syn_A.json",
        "synB": "tmp/syn_B.json",
        "keyA": "tmp/key_A.json",
        "keyB": "tmp/key_B.json"
    }


# ==============================
# LOAD DATA
# ==============================
def load_data():
    data = []
    with open("test.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                try:
                    data.append((int(row[0]), row[1].strip()))
                except:
                    pass
    return data


# ==============================
# SIMPLE ACCURACY
# ==============================
def compute_accuracy(model, data):
    correct = 0
    for label, text in data:
        if model.predict_one(text) == label:
            correct += 1
    return round((correct / len(data)) * 100, 2)


# ==============================
# MAIN EXPERIMENT SCRIPT
# ==============================
def main():
    files = create_demo_files()
    data = load_data()

    # pick 1 random tweet
    true_label, tweet = random.choice(data)

    print("\n🎯 RANDOM TWEET")
    print("True label:", true_label)
    print("Tweet:", tweet)
    print("="*80)

    results = []

    # ============================================================
    # 🔵 1. KNN EXPERIMENTS
    # ============================================================
    manager.select("KNN")
    knn = manager.get_current()

    print("\n\n🔵 TESTING KNN\n")

    # --- k values ---
    for k in [1, 3, 7]:
        knn.set_params(k=k, synonyms_path=files["synA"])
        knn.fit(data)
        pred = knn.predict_one(tweet)
        acc = compute_accuracy(knn, data)

        results.append(["KNN", "k", str(k), pred, acc])
        print(f"KNN (k={k}) → pred={pred}, acc={acc}%")


    # --- Distances (wrapper only supports 'jaccard', others ignored)
    for dist in ["jaccard"]:
        knn.set_params(k=3, distance=dist, synonyms_path=files["synA"])
        knn.fit(data)
        pred = knn.predict_one(tweet)
        acc = compute_accuracy(knn, data)

        results.append(["KNN", "distance", dist, pred, acc])
        print(f"KNN (dist={dist}) → pred={pred}, acc={acc}%")


    # --- Synonyms file ---
    for syn in [files["synA"], files["synB"]]:
        knn.set_params(k=3, distance="jaccard", synonyms_path=syn)
        knn.fit(data)
        pred = knn.predict_one(tweet)
        acc = compute_accuracy(knn, data)

        results.append(["KNN", "synonyms", syn, pred, acc])
        print(f"KNN (syn={syn}) → pred={pred}, accuracy={acc}%")


    # ============================================================
    # 🟣 2. KEYWORD EXPERIMENTS
    # ============================================================
    manager.select("Keyword")
    kw = manager.get_current()

    print("\n\n🟣 TESTING KEYWORDS\n")

    # --- Keyword files ---
    for key in [files["keyA"], files["keyB"]]:
        kw.set_params(keywords_path=key)
        kw.fit()
        pred = kw.predict_one(tweet)
        acc = compute_accuracy(kw, data)

        results.append(["Keyword", "keywords", key, pred, acc])
        print(f"Keyword ({key}) → pred={pred}, acc={acc}%")


    # --- Threshold ---
    for thr in [0.0, 0.3, 0.9]:
        kw.set_params(threshold=thr)
        kw.fit()
        pred = kw.predict_one(tweet)
        acc = compute_accuracy(kw, data)

        results.append(["Keyword", "threshold", str(thr), pred, acc])
        print(f"Keyword (thr={thr}) → pred={pred}, acc={acc}%")


    # ============================================================
    # 🟡 3. NAIVE BAYES EXPERIMENTS
    # ============================================================
    manager.select("Naive Bayes")
    nb = manager.get_current()

    print("\n\n🟡 TESTING NAIVE BAYES\n")

    # Try different smoothing values (even if teammate does not use them)
    for s in [0.5, 1.0, 2.0]:
        nb.set_params(smoothing=s)
        nb.fit(data)
        pred = nb.predict_one(tweet)
        acc = compute_accuracy(nb, data)

        results.append(["Naive Bayes", "smoothing", str(s), pred, acc])
        print(f"NaiveBayes (smooth={s}) → pred={pred}, acc={acc}%")


    # ============================================================
    # 📊 FINAL TABLE
    # ============================================================
    print("\n\n" + "="*80)
    print("📊 FINAL RESULTS TABLE")
    print("="*80)

    print(f"{'Algo':<12} | {'Param':<12} | {'Value':<20} | Pred | Acc")
    print("-"*80)
    for algo, param, value, pred, acc in results:
        print(f"{algo:<12} | {param:<12} | {value:<20} | {pred:<4} | {acc}%")

    print("="*80)


if __name__ == "__main__":
    main()
