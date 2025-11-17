# 📘 README — Algorithm Wrappers & Manager System

## 🧩 Overview

This module provides a fully-generic, extensible system for integrating **multiple sentiment-analysis algorithms** under a single abstraction layer.

It solves the biggest challenge in our PJE project:

> **Different algorithms expect different inputs, parameters, and produce different outputs.**

To fix this, we introduce:

- **Algorithm Wrappers** → One class per algorithm  
- **Algorithm Manager** → Central controller that switches between algorithms  
- **Param Schema** → Structured configuration for each algorithm  
- **Unified Evaluation** → Standard accuracy pipeline  
- **Streamlit GUI Integration** → Parameters & algorithm selection generated dynamically  

The result is a **plug-and-play architecture**:
you can switch between Keyword Annotation, KNN, Naive Bayes, and Clustering **in one line of code** or **one click in GUI**, without rewriting logic.

---

## 🏗 Architecture

```
core/
 ┣ algorithm_wrapper.py     ← BaseAlgorithm, KNNWrapper, KeywordWrapper
 ┣ algorithm_manager.py     ← Central controller
algorithms/
 ┣ knn/                     ← KNN implementation, distances, synonyms
 ┣ keywords/                ← Keyword annotation implementation
demo/
 ┣ demo_experiments.py      ← Full parameter-testing experiment
```

---

## 🎯 Why This System Is Needed

### 1. Algorithms are heterogeneous  
Each algorithm requires different:
- input format  
- resources (keywords, synonyms)  
- parameters  
- output types  

Without wrappers, the GUI must implement special-case logic for each algorithm.

### 2. Wrappers unify everything  
Every wrapper implements:

- `fit(data)`  
- `predict_one(text)`  
- `predict_batch(texts)`  
- `set_params(**kwargs)`  
- `evaluate(dataset)`  
- `describe()`  

This makes all algorithms interchangeable.

### 3. AlgorithmManager coordinates everything  
The GUI or backend does:

```python
manager.select("KNN")
manager.fit(data)
prediction = manager.predict_one("I love my Kindle")
```

This allows:
- switching algorithms dynamically  
- consistent training/prediction logic  
- clean Streamlit integration  

---

## 🧱 BaseAlgorithm

All algorithms inherit from this:

```python
class BaseAlgorithm:
    def fit(self, data): ...
    def predict_one(self, text): ...
    def predict_batch(self, texts): ...
    def evaluate(self, dataset): ...
    def set_params(self, **kwargs): ...
```

Wrappers override only what they need.

---

## 🔵 KNNWrapper

- **Supervised**  
- Parameters:
  - `k`  
  - `distance` (jaccard, cosine, levenshtein, euclidean, manhattan)  
  - `synonyms_path`  
- Builds:
  - `JaccardDistance` (or others)
  - `MajorityVote`
  - `KNNClassifier`

Used in GUI:
- Streamlit slider for `k`
- Dropdown for distance metric
- File picker for synonyms JSON

---

## 🟣 KeywordWrapper

- **Rule-based**
- Parameters:
  - `keywords_path`
  - `threshold`
- Uses:
  - `KeywordAnnotator`
  - `AnnotationParams`
  - `annotate_tweet()`

Used in GUI:
- File picker for keyword JSON  
- Slider for threshold  

---

## 📊 Evaluation

BaseAlgorithm provides shared evaluation:

```python
result = manager.evaluate(dataset)
```

Returns:

```json
{
  "accuracy": 67.21,
  "correct": 1293,
  "total": 1923
}
```

GUI can display:
- Accuracy %
- Confusion matrix
- Prediction samples
- Detailed stats

---

## 🖥 Streamlit Integration

### 1. List available algorithms

```python
algo = st.selectbox("Choose an algorithm", manager.get_available_algos())
manager.select(algo)
```

### 2. Load the parameter schema

```python
params = manager.get_current().param_schema
```

### 3. Auto-generate GUI controls

For each param:

| type      | Streamlit widget |
|-----------|------------------|
| int       | slider           |
| float     | slider           |
| select    | dropdown         |
| file      | file uploader    |

Then:

```python
model.set_params(**updated_values)
```

### 4. Prediction

```python
prediction = manager.predict_one(tweet)
```

### 5. Evaluation

```python
result = manager.evaluate(dataset)
st.metric("Accuracy", f"{result['accuracy']}%")
```

---

## 🚀 Adding New Algorithms

To add **Naive Bayes**, **Clustering**, or any ML model:

### Step 1 — Create a new wrapper

```python
class NaiveBayesWrapper(BaseAlgorithm):
    name = "Naive Bayes"
    mode = "supervised"
    output_type = "label"

    def __init__(self):
        super().__init__()
        self.param_schema = {...}
        self.params = {...}
        self.model = None

    def fit(self, data):
        self.model = NaiveBayes(...)
        self.model.train(data)

    def predict_one(self, text):
        return self.model.predict(text)
```

### Step 2 — Add it to the manager

```python
manager = AlgorithmManager([
    ("KNN", KNNWrapper()),
    ("Keyword", KeywordWrapper()),
    ("Naive Bayes", NaiveBayesWrapper())
])
```

### Step 3 — GUI automatically picks it up  
No changes needed in Streamlit code.

---

## 🤖 Future Algorithms

### ✔ Naive Bayes
- Uses token probabilities  
- Parameters: smoothing, tokenizer, stopwords  
- Same wrapper pattern  

### ✔ Clustering
- Unsupervised  
- Output: cluster ID  
- Wrapper still works because:
  - prediction = assign cluster  
  - evaluation = silhouette score or “N/A”  

The same architecture continues to work.

---

## 🧪 Demo Experiments

`demo_experiments.py` runs:

- Multiple KNN configurations  
- Multiple Keyword configurations  
- Computes:
  - prediction on random tweet  
  - accuracy on whole dataset  
- Produces a final comparison table  

This is used for:
- hyperparameter search  
- debugging  
- benchmarking  
- GUI validation  

---

## ✔ Summary

This system provides:

### 🟩 Clean separation of concerns  
- Wrappers focus on algorithm logic  
- Manager controls selection & execution  
- GUI reads param schema  
- Evaluation is standardized  

### 🟩 Unlimited extensibility  
Add new algorithms in minutes, with zero GUI changes.

### 🟩 A professional, maintainable architecture  
Perfect for the PJE submission and future extension.

