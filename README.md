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
├── requirements.txt             # Pinned web app dependencies for deployment
├── requirements-training.txt    # Optional plotting dependency for model evaluation
├── .gitignore                   # Excludes Python caches and local secrets
├── train_model.py               # Logistic Regression training & evaluation script
├── roc_curve_binary.png         # Binary classification ROC-AUC curve plot
├── roc_curve_multiclass.png     # Multi-class One-vs-Rest ROC-AUC curves plot
├── .streamlit/config.toml       # Enables local static assets for the 3D Discover hero
├── static/hero.css              # Hero-only styles, responsive and motion fallbacks
├── static/hero3d.js              # Three.js reel, ribbon, particle, and poster scene
├── static/heroScroll.js          # GSAP/ScrollTrigger scenes and Lenis integration
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
- **No account barrier**: Open the local app directly; no demo login or sign-up is required.
- **Cinematic responsive interface**: Dark editorial styling, a scroll-driven Three.js film-reel hero, animated ambient lighting, and genre-colour catalogue artwork.
- **Dataset-Backed Recommendations**: Suggestions are selected from `movies_featured.csv`, using its genre, era, year, and engineered metadata.
- **Similar-Movie Recommendations**: TF-IDF vectorization and cosine similarity rank movies by title, genre, franchise, decade, and era metadata.
- **Genre and Era Filters**: Search and filter on fields present in the catalogue.
- **User Watchlist**: Session-persisted watchlist keyed by the dataset's `movieId`; no account or permanent storage is used.
- **Catalogue Explorer**: Search the full 62,423-record dataset, browse it in pages, and download filtered results.
- **AI Lab**: Inspect and export the loaded dataset and learn how the rule-based filters and content-similarity model work.

The current MovieLens-derived CSV does not contain ratings, language, director, runtime, plot descriptions, or mood. The web app does not invent or display those details, and it does not fetch data from a live movie API. Similarity is content-based; the app does not train on user ratings or use a generative AI model. Streamlit serves the Python interface; it is not required by the recommendation-data pipeline itself.

---

## ⚡ Installation & Quickstart

### 1. Prerequisites
Use Python 3.13 to match the pinned and tested dependencies.

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
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
pip install -r requirements-training.txt
python train_model.py
```
*Outputs: Evaluation metrics in terminal, `roc_curve_binary.png`, and `roc_curve_multiclass.png`*

### 6. Launch Web Application
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`. No login is required.

### Deploy for free on Streamlit Community Cloud

The repository is prepared for Streamlit Community Cloud:

1. Push the project to a GitHub repository and include `app.py`, `requirements.txt`, `.streamlit/config.toml`, `static/`, and `movies_featured.csv`.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py` as the entrypoint.
3. Select Python 3.13 and deploy. Community Cloud installs the pinned app dependencies from `requirements.txt`.

The 25 MB featured CSV is loaded locally by the app; it is not downloaded from an external service. The 3D hero imports Three.js, GSAP, and Lenis from esm.sh, so browser access to that CDN is required. Free Community Cloud apps may sleep when unused and have resource limits; deployment availability and cold-start time depend on the platform.

### The Film Reel Journey

The Discover page's hero is implemented in `static/hero3d.js` (Three.js scene), `static/heroScroll.js` (GSAP ScrollTrigger scenes and Lenis scrolling), and `static/hero.css`. It uses Streamlit's static-file serving, enabled in `.streamlit/config.toml`. Internet access is required for the browser modules hosted by esm.sh.

- **Reel model**: the app attempts to load `static/assets/reel.glb` (served at `/app/static/assets/reel.glb`). If it is absent or cannot load, the six-opening metallic reel is generated in Three.js.
- **Poster source**: the current `movies_featured.csv` has no image URLs or popularity/rating field, and the app has no movie-poster API. The hero therefore makes 12 512 × 700 title/genre poster textures from real catalogue metadata and displays them as a larger curved wall (six across on desktop, three across on mobile). If a `poster_url` or `posterUrl` column is added, the hero loads and downsizes those images, falling back to the generated artwork when an image cannot load. Supply image URLs from a source you are authorized to use; cross-origin image servers must permit canvas access.
- **Featured catalogue selection**: recognizable titles are selected only when they exist in the local dataset; remaining slots are filled from its records. This is display content for the hero and does not change recommendation ranking.
- **Motion and fallback**: the scroll journey pins for 190% of the scroll-container height (about 1.9 viewport lengths); the cinematic section is full-bleed at 100vw. Users with reduced-motion enabled see a static hero, and WebGL or module-loading failures also fall back to static content. The “Start Discovering” CTA jumps to the existing dataset stats. The poster details dialog shows the selected MovieLens metadata; no detail page exists elsewhere in this app.

---

## 📄 License
This project is open-source and intended for educational and portfolio demonstration purposes.