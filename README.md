# Customer Review Intelligence Platform

A full-stack AI application for investigating customer feedback at scale. It combines a trained sentiment classifier, semantic retrieval over 306,316 reviews, Gemini-grounded RAG answers, and interactive product analytics.

## What it includes

- Executive dashboard for review volume, sentiment, ratings, and top products
- Sentiment prediction using the existing TF-IDF and Logistic Regression artifacts
- RAG assistant with semantic retrieval from the existing ChromaDB collection
- Product-level ratings, sentiment, review evidence, AI summaries, and comparisons
- Review explorer with keyword search, semantic search, filters, and pagination
- Responsive dark-mode UI with loading, empty, and error states

## Prerequisites

- Python 3.11+ (the included environment uses Python 3.11)
- Node.js 20+
- A Gemini API key for generated RAG answers and AI product summaries

The repository already contains the trained models, processed dataset, and persistent vector database. Do not retrain or regenerate them to run the application.

## Configure the backend

From the repository root, create a `.env` file based on [`backend/.env.example`](backend/.env.example):

```env
GEMINI_API_KEY=your_key_here
```

The default paths expect these existing artifacts:

- `models/sentiment_model.pkl`
- `models/tfidf_vectorizer.pkl`
- `vector_db/`
- `data/processed/cleaned_reviews.csv`

Install dependencies and start the API:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --reload --port 8000
```

Open `http://localhost:8000/docs` to inspect the API.

## Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite development server proxies `/api` requests, while the client defaults to `http://localhost:8000` when `VITE_API_URL` is not set. To override it, create `frontend/.env` from [`frontend/.env.example`](frontend/.env.example).

## Validate a production build

```powershell
cd frontend
npm run build
```

## API surface

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/predict-sentiment` | Classify review sentiment with confidence and probabilities |
| `POST` | `/ask-ai` | Retrieve review evidence and generate a grounded answer |
| `GET` | `/dashboard` | Return platform-level KPIs and chart data |
| `GET` | `/products` | List product aggregates with optional search |
| `GET` | `/product/{product_name}` | Return detailed product intelligence |
| `GET` | `/reviews` | Explore reviews using filters or semantic search |
| `POST` | `/compare-products` | Compare two product review profiles |

## Project structure

```text
backend/                 FastAPI app and ML/RAG/analytics services
data/processed/          Existing review dataset used for analytics
models/                  Existing sentiment model and TF-IDF vectorizer
vector_db/               Existing ChromaDB review embeddings
frontend/src/pages/      Routed application screens
frontend/src/components/ Reusable UI building blocks
```
