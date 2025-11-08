# 🧩 Algorithm Wrappers & Dataset Abstraction — Problem & Design Motivation

## 🎯 Context

In the “Analyse de sentiments sur Twitter” project, multiple algorithms are developed and evaluated over the same data — from simple rule-based methods to machine learning approaches.

However, each algorithm:
- expects different input formats,
- requires distinct parameters,
- and produces results in various forms (labels, probabilities, clusters).

This diversity makes it **difficult to integrate, compare, and reuse** these methods inside a unified application (GUI or web interface).

---

## 🚨 The Core Problem: Heterogeneous Algorithms

Each algorithm works independently but speaks its own “language.”  
Their expectations vary across data structure, supplementary parameters, and output style.

| Algorithm | Needs Labels? | Input Type | Supplementary Parameters | Output | Nature |
|------------|---------------|-------------|----------------------------|---------|--------|
| **Keyword Annotation** | ✅ Yes | `list[(tweet, label)]` | Keyword lists (positive/negative), thresholds | Labels | Rule-based |
| **KNN** | ✅ Yes | `list[(label, tweet)]` | `k`, distance metric (Jaccard, Cosine, etc.), voting type, synonym list | Labels | Supervised |
| **Naive Bayes** | ✅ Yes | `(X, y)` or `list[(label, tweet)]` | Smoothing constant, tokenizer, stopword list | Labels + Probabilities | Supervised |
| **Clustering** | ❌ No | `list[tweet]` | Distance matrix or TF-IDF model, linkage method, number of clusters | Cluster IDs | Unsupervised |

Because of these differences:
- Every new algorithm requires custom integration logic.
- GUI components must handle special cases per algorithm.
- Comparing models becomes tedious and error-prone.

---

## 💡 Design Objective

To solve this, the next phase of the project will introduce **Algorithm Wrappers** — lightweight abstractions that define a *common structure* for all algorithms.  
Each wrapper will encapsulate:
- how the algorithm trains (`fit`),
- how it predicts (`predict_one`, `predict_batch`),
- and what parameters it needs (`params`, `config`).

Similarly, a **Dataset Abstraction** will serve as the bridge between files and models.  
This ensures that all algorithms consume the same standardized data type, no matter how the CSV or preprocessing differs.

---

## 🧱 Conceptual Architecture

```
data/
 ┣ tweets_cleaned.csv
core/
 ┣ dataset.py         ← loads, validates, and splits data
 ┣ base_algorithm.py  ← defines the abstract interface
algorithms/
 ┣ knn_wrapper.py
 ┣ keyword_wrapper.py
 ┣ bayes_wrapper.py
 ┣ clustering_wrapper.py
ui/
 ┣ app.py (GUI / Web)
 ┗ components/
utils/
 ┣ evaluation.py      ← shared metrics
 ┣ plotting.py        ← performance visualization
```

This modular design will allow the GUI or command-line interface to call **any algorithm** through the same entry points — reducing complexity while improving maintainability and clarity.

---

## 🧭 Expected Outcomes

By applying this architecture:
- All algorithms become **interchangeable and testable** under the same interface.  
- The GUI can dynamically display algorithm parameters.  
- Evaluation and comparison scripts are **generic**, not rewritten per model.  
- The project is **future-proof** for upcoming algorithms (Bayes, Clustering, etc.).

---

This redesign isn’t about adding new functionality yet —  
it’s about defining a **solid, extensible foundation** that simplifies integration, evaluation, and visualization later in the PJE pipeline.
