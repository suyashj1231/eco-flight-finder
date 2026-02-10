# Eco Flight Finder

Find flights and rank results with eco-focused signals like estimated CO2 emissions.

## Quick Start

### 1) Configure environment

Create a `.env` file at the project root with your AviationStack API key:

```
API_KEY=your_aviationstack_key
```

Optional (CORS for local frontend dev):

```
FRONTEND_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2) Start the backend (FastAPI)

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload
```

The API will be available at http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

### 3) Start the frontend (Vite + React)

```
cd front-end
npm install
npm run dev
```

Open http://localhost:5173

## CLI (optional)

Run the CLI search flow:

```
cd backend
python main.py
```

## Notes

- The free AviationStack plan has limited date filtering. For some dates the API may return only active or recent flights.
- Ensure the backend is running before using any frontend features that call the API.