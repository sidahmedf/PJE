# algorithms.py
from knn.knn_classifier import KNNClassifier
from knn.distance import JaccardDistance
from knn.voting import MajorityVote
from keywords.annotator import KeywordAnnotator
from keywords.evaluate import evaluate_accuracy


# ============================================================
# 🧱 Base Class
# ============================================================
class BaseAlgorithm:
    """Defines a common interface for all algorithms."""

    name = "BaseAlgorithm"
    mode = "abstract"
    output_type = None
    description = "Abstract algorithm wrapper"

    def __init__(self):
        self.param_schema = {}
        self.params = {}

    # ---- Parameter Handling ----
    def get_params(self):
        return self.params

    def set_params(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.param_schema:
                self.params[k] = v

    # ---- Core Methods ----
    def fit(self, data):
        raise NotImplementedError

    def predict_one(self, text):
        raise NotImplementedError

    def predict_batch(self, texts):
        return [self.predict_one(t) for t in texts]

    def evaluate(self, dataset):
        """Generic evaluator for supervised algorithms using (label, text) pairs."""
        if not dataset:
            return {"error": "Empty dataset"}

        correct = 0
        total = 0
        for true_label, tweet in dataset:
            try:
                pred = self.predict_one(tweet)
                if pred == true_label:
                    correct += 1
                total += 1
            except Exception as e:
                print(f"⚠️ Prediction error on tweet: {tweet[:30]}... ({e})")

        accuracy = correct / total * 100 if total > 0 else 0
        return {"accuracy": round(accuracy, 2), "correct": correct, "total": total}

    def describe(self):
        return {
            "name": self.name,
            "mode": self.mode,
            "params": self.params,
            "output_type": self.output_type,
        }


# ============================================================
# 🧩 KNN Wrapper
# ============================================================
class KNNWrapper(BaseAlgorithm):
    name = "KNN"
    mode = "supervised"
    output_type = "label"
    description = "K-Nearest Neighbors classifier (Jaccard distance)"

    def __init__(self, **kwargs):
        super().__init__()
        self.param_schema = {
            "k": {"type": "int", "min": 1, "max": 20, "default": 5},
            "distance": {"type": "select", "options": ["jaccard"], "default": "jaccard"},
            "synonyms_path": {"type": "file", "default": "data/synonyms.json"},
        }
        self.params = {k: v["default"] for k, v in self.param_schema.items()}
        self.params.update(kwargs)
        self.knn = None

    def fit(self, data):
        """Prepare and store training data."""
        distance = JaccardDistance(
            use_synonyms=True,
            synonym_json=self.params["synonyms_path"]
        )
        voter = MajorityVote()
        self.knn = KNNClassifier(
            k=self.params["k"], distance=distance, voter=voter
        )
        self.knn.fit(data)

    def predict_one(self, text):
        return self.knn.predict_one(text)


# ============================================================
# 🧩 Keyword Annotation Wrapper
# ============================================================
class KeywordWrapper(BaseAlgorithm):
    name = "Keyword Annotation"
    mode = "rule-based"
    output_type = "label"
    description = "Rule-based keyword sentiment annotator"

    def __init__(self, **kwargs):
        super().__init__()
        self.param_schema = {
            "keywords_path": {"type": "file", "default": "data/keywords.json"},
            "threshold": {"type": "float", "default": 0.1},
        }
        self.params = {k: v["default"] for k, v in self.param_schema.items()}
        self.params.update(kwargs)
        self.annotator = None

    def fit(self, data=None):
        """Load keyword resources."""
        self.annotator = KeywordAnnotator(json_path=self.params["keywords_path"])

    def predict_one(self, tweet):
        """
        Predict a single tweet by reusing the annotator's real logic
        (annotate_tweet + params), without modifying KeywordAnnotator.
        """
        from keywords.annotation import annotate_tweet

        return annotate_tweet(tweet, self.annotator.params)

