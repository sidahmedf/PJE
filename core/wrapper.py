# core/wrapper.py
from algorithms.knn.knn_classifier import KNNClassifier
from algorithms.knn.distance import JaccardDistance
from algorithms.knn.voting import MajorityVote
from algorithms.keywords.annotator import KeywordAnnotator
from algorithms.bayes.bayes import train_naive_bayes, classify
# --- Import du Clustering ---
from algorithms.clustering.hierarchical import ClusteringHierarchique
import random


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
        from algorithms.keywords.annotation import annotate_tweet
        return annotate_tweet(tweet, self.annotator.params)


# ============================================================
# 🧩 Naive Bayes Wrapper
# ============================================================
class NaiveBayesWrapper(BaseAlgorithm):
    name = "Naive Bayes"
    mode = "supervised"
    output_type = "label"
    description = "Naive Bayes classifier"

    def __init__(self, **kwargs):
        super().__init__()
        self.param_schema = {
            "smoothing": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 5.0,
                "step": 0.1,
            }
        }
        self.params = {k: v["default"] for k, v in self.param_schema.items()}
        self.params.update(kwargs)

        self.prior = None
        self.cond_prob = None
        self.vocab = None

    def fit(self, data):
        converted = [(text, label) for label, text in data]
        self.prior, self.cond_prob, self.vocab = train_naive_bayes(converted)

    def predict_one(self, text):
        if self.prior is None:
            raise ValueError("Naive Bayes must be trained before predicting.")
        return classify(text, self.prior, self.cond_prob, self.vocab)


# ============================================================
# 🧩 Dummy Wrappers
# ============================================================
class DummyWrapper(BaseAlgorithm):
    name = "Dummy"
    mode = "supervised"
    output_type = "label"
    description = "Dummy algorithm returning random predictions"

    def __init__(self, possible_labels=None, **kwargs):
        super().__init__()
        self.param_schema = {
            "possible_labels": {"type": "list", "default": [0, 2, 4]}
        }
        self.params = {k: v["default"] for k, v in self.param_schema.items()}
        self.params.update(kwargs)
        self.possible_labels = self.params["possible_labels"]

    def fit(self, data):
        pass

    def predict_one(self, text):
        return random.choice(self.possible_labels)


class DummyAlgo2(BaseAlgorithm):
    name = "Dummy Always 4"
    mode = "supervised"
    output_type = "label"
    description = "Deterministic algorithm that always predicts label 4"

    def __init__(self, **kwargs):
        super().__init__()
        self.param_schema = {}
        self.params = {}
        self.params.update(kwargs)

    def fit(self, data):
        pass

    def predict_one(self, text):
        return 4


# ============================================================
# 🧶 Clustering Wrapper (AJOUTÉ)
# ============================================================
class ClusteringWrapper(BaseAlgorithm):
    name = "Hierarchical Clustering"
    mode = "unsupervised"
    output_type = "cluster_id"
    description = "Pipelines cours: Jaccard (Avg/Comp) & Ward (TF-IDF)"

    def __init__(self, **kwargs):
        super().__init__()
        self.param_schema = {
            "n_clusters": {"type": "int", "min": 2, "max": 10, "default": 3},
            "linkage": {"type": "select", "options": ["ward", "average", "complete"], "default": "ward"}
        }
        self.params = {k: v["default"] for k, v in self.param_schema.items()}
        self.params.update(kwargs)
        self.algo = None

    def fit(self, data):
        # data est une liste de tuples (label, tweet)
        # On extrait juste les textes pour le clustering
        textes = [t for _, t in data]

        self.algo = ClusteringHierarchique(
            n_clusters=self.params["n_clusters"],
            methode_lien=self.params["linkage"]
        )
        self.algo.entrainer(textes)

    def predict_one(self, text):
        if self.algo:
            return self.algo.predire_un(text)
        return -1

    # Méthodes spécifiques pour l'interface graphique
    def get_linkage_matrix(self):
        return self.algo.recuperer_donnees_lien() if self.algo else None

    def get_labels(self):
        return self.algo.labels_ if self.algo else []