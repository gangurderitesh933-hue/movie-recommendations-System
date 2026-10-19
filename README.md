# 🎬 CineSuggest AI | Movie Recommendation & Machine Learning System

An end-to-end Movie Recommendation System powered by Python, Scikit-Learn, and Streamlit. The project covers data preprocessing, advanced feature engineering, model training using **Logistic Regression (L2 Regularized)**, performance evaluation across multiple error metrics, and an interactive web interface.

---

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [Repository Structure](#-repository-structure)
- [Dataset Profile & Analysis](#-dataset-profile--analysis)
- [Data Preprocessing Pipeline](#-data-preprocessing-pipeline)
- [Feature Engineering](#-feature-engineering)
- [Model Training & Evaluation (Logistic Regression)](#-model-training--evaluation-logistic-regression)
- [Interactive Streamlit Web App](#-interactive-streamlit-web-app)
- [Installation & Quickstart](#-installation--quickstart)

---

## 🚀 Project Overview

This repository transforms the MovieLens 25M movie collection (62,423 titles) into an intelligent, content-driven movie recommendation and classification system:
1. **Data Cleaning & Normalization**: Cleans raw text, extracts release years from titles, restores inverted grammatical articles, and binarizes multi-label genres.
2. **Feature Engineering**: Constructs 16 high-signal features spanning temporal eras, franchise roots, genre synergy/rarity scores, and weighted recommendation soups.
3. **Machine Learning**: Implements **Logistic Regression (Multinomial with L2 Regularization)**, benchmarked against rigorous metrics (**Accuracy, Precision, Recall, F1-Score, Matthews Correlation Coefficient (MCC), and ROC-AUC**).
4. **Interactive UI**: A rich dark-mode Streamlit dashboard with movie discovery, watchlist management, and transparent recommendation logic.

---

## 📂 Repository Structure

```
├── movies.csv                   # Raw MovieLens dataset (62,423 movies, 3 columns)
├── preprocess.py                # Data cleaning, year extraction & genre binarization
├── movies_preprocessed.csv      # Preprocessed dataset (62,423 rows, 30 columns)
├── feature_engineering.py       # Advanced feature engineering pipeline
├── movies_featured.csv          # Final feature-engineered dataset (45 columns)
├── train_model.py               # Logistic Regression training & evaluation script
├── roc_curve_binary.png         # Binary classification ROC-AUC curve plot
├── roc_curve_multiclass.png     # Multi-class One-vs-Rest ROC-AUC curves plot
├── app.py                       # Interactive Streamlit web application
└── README.md                    # Project documentation
```

---

## 📊 Dataset Profile & Analysis

- **Total Records**: **62,423** movies
- **Raw Attributes**: `movieId`, `title`, `genres`
- **Release Timeline**: **1874 to 2019** (Median year: **2002**)
- **Unique Genres**: **19** distinct genres (plus *(no genres listed)*)

### Top Genre Distribution
| Genre | Movie Count | % of Catalogue |
| :--- | :---: | :---: |
| **Drama** | 25,606 | 41.02% |
| **Comedy** | 16,870 | 27.03% |
| **Thriller** | 8,654 | 13.86% |
| **Romance** | 7,719 | 12.37% |
| **Action** | 7,348 | 11.77% |
| **Horror** | 5,989 | 9.59% |
| **Documentary** | 5,605 | 8.98% |
| **Crime** | 5,319 | 8.52% |

---

## 🛠️ Data Preprocessing Pipeline

Implemented in [`preprocess.py`](preprocess.py):

1. **Release Year Extraction**: Uses regular expressions (`r'\((\d{4})\)'`) to extract 4-digit release years from title strings into a nullable integer column (`year`).
2. **Title Inversion Correction**: Standardizes inverted grammatical articles:
   - `"Matrix, The (1999)"` $\rightarrow$ `"The Matrix"`
   - `"American President, The (1995)"` $\rightarrow$ `"The American President"`
3. **Resilient Search Key**: Generates `search_title` (lowercase, alphanumeric only) for robust fuzzy query lookups.
4. **Genre Parsing & One-Hot Encoding**: Replaces `(no genres listed)` with null flags and creates 19 binary indicator columns (`genre_action`, `genre_comedy`, `genre_drama`, etc.).
5. **Metadata Soup**: Produces an initial combined text profile (`clean_title + genres + year`) for content-based similarity.

---

## 🧠 Feature Engineering

Implemented in [`feature_engineering.py`](feature_engineering.py), adding **16 new features** (expanding the dataset from 29 to 45 columns):

| Category | Features Added | Description |
| :--- | :--- | :--- |
| **Temporal & Era** | `decade`, `era`, `movie_age` | Categorizes films into decade buckets and cinematic movements (*Silent / Pioneer*, *Golden Age*, *New Hollywood*, *Modern Classic*, *Contemporary*, *Recent*). |
| **Genre Synergy** | `primary_genre`, `genre_combo`, `is_single_genre`, `is_multi_genre`, `genre_rarity_score` | Captures the primary thematic anchor, exact alphabetical genre signatures, and an IDF-weighted rarity score. |
| **Franchise & Linguistics** | `is_sequel_or_franchise`, `franchise_root`, `has_subtitle`, `has_alternate_title`, `alternate_title`, `title_word_count`, `title_char_length` | Identifies sequels/installments and extracts root intellectual property (e.g. `"The Godfather"` from `"The Godfather: Part II"`). |
| **Weighted Vectorization** | `weighted_metadata_soup` | Formulates an optimized token string ($2\times \text{Title} + \text{Franchise Root} + 2\times \text{Primary Genre} + \text{All Genres} + \text{Decade} + \text{Era}$) designed for TF-IDF / Cosine distance matching. |

---

## 🤖 Model Training & Evaluation (Logistic Regression)

Implemented in [`train_model.py`](train_model.py):

- **Algorithm**: `LogisticRegression` (L2 Penalty, $C=1.0$, `lbfgs` solver)
- **Loss Formulation**:
  $$\min_{\mathbf{w}} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{i=1}^N \log \left(1 + \exp(-y_i \mathbf{w}^T \mathbf{x}_i)\right)$$
- **Feature Vectorizer**: TF-IDF N-gram Vectorizer (1-2 ngrams, 4,000 features) on engineered movie metadata.

### 1. Binary Classification (Action vs. Non-Action)
Evaluated on a stratified hold-out test set ($N_{\text{test}} = 6,000$):

| Metric | Score | Note |
| :--- | :---: | :--- |
| **Accuracy** | **0.8843** (88.43%) | Total correct predictions across both classes |
| **Precision** | **0.7143** (71.43%) | High positive predictive value for action genre |
| **Recall** | **0.0283** (2.83%) | Conservative positive detection rate |
| **F1 Score** | **0.0545** | Harmonic mean of precision & recall |
| **Matthews Correlation Coefficient (MCC)** | **+0.1268** | Quality metric robust to class imbalance |
| **ROC AUC** | **0.7318** 🏆 | High discriminative area under the ROC curve |

*ROC Curve saved to: [`roc_curve_binary.png`](roc_curve_binary.png)*

---

### 2. Multi-Class Classification (Top 5 Genres: Drama, Comedy, Action, Documentary, Horror)
Evaluated on $N_{\text{test}} = 5,000$:

| Metric | Score | Random Baseline |
| :--- | :---: | :---: |
| **Overall Accuracy** | **0.4434** (44.34%) | 0.2000 (20.00%) |
| **Weighted Precision** | **0.4471** (44.71%) | — |
| **Weighted Recall** | **0.4434** (44.34%) | — |
| **Weighted F1 Score** | **0.4175** | — |
| **Matthews Correlation Coefficient (MCC)** | **+0.2160** | 0.0000 |
| **ROC AUC (Weighted OvR)** | **0.6881** 🏆 | 0.5000 |

*One-vs-Rest Multi-Class ROC Curves saved to: [`roc_curve_multiclass.png`](roc_curve_multiclass.png)*

---

## 💻 Interactive Streamlit Web App

The application in [`app.py`](app.py) provides a modern, dark-themed UI featuring:
- **Personalized Recommendations**: Instant suggestions based on genre, language, mood, and minimum rating.
- **Rule-Based & Semantic Scoring**: Transparent explanations for why each film is recommended.
- **User Watchlist**: Session-persisted watchlist for saving films.
- **Catalogue Explorer**: Searchable movie library with tabular export to CSV.
- **AI Lab**: Interactive sandbox to test scoring weights and explore the movie knowledge base.

---

## ⚡ Installation & Quickstart

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```powershell
pip install pandas numpy scikit-learn matplotlib streamlit
```

### 3. Run Preprocessing Pipeline
```powershell
python preprocess.py
```
*Outputs: `movies_preprocessed.csv`*

### 4. Run Feature Engineering Pipeline
```powershell
python feature_engineering.py
```
*Outputs: `movies_featured.csv`*

### 5. Train Logistic Regression Model & Generate ROC Curves
```powershell
python train_model.py
```
*Outputs: Evaluation metrics in terminal, `roc_curve_binary.png`, and `roc_curve_multiclass.png`*

### 6. Launch Web Application
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`. Demo credentials: `demo` / `movie123`.

---

## 📄 License
This project is open-source and intended for educational and portfolio demonstration purposes.