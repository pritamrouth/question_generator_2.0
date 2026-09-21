# Question Generation System

An AI-powered assessment content engine that transforms unstructured educational materials — PDFs, images, URLs, and raw text — into structured, pedagogically-aligned question sets using Google Gemini 1.5 via LangChain.

Built for EdTech platforms, L&D teams, and content authoring workflows that demand configurable, scalable question generation with curriculum-aligned taxonomy support.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                           │
│                  Tailwind CSS · Vanilla JS · Jinja2                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  POST /generate (multipart/form-data)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FLASK API SERVER (Python 3.9)                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Input Router │  │  QuestionEngine  │  │  Response Formatter  │  │
│  │  (app.py)     │──│  (LangChain)     │──│  (JSON)              │  │
│  └──────┬───────┘  └────────┬─────────┘  └──────────────────────┘  │
│         │                   │                                      │
│         ▼                   ▼                                      │
│  ┌──────────────┐  ┌──────────────────┐                            │
│  │  Extraction  │  │  Output Parser   │                            │
│  │  Pipeline    │  │  (Pydantic)      │                            │
│  └──────┬───────┘  └──────────────────┘                            │
│         │                                                          │
│  ┌──────┴────────────────────────────┐                             │
│  │  Text Extraction Adapters         │                             │
│  │  ├─ PyPDF2       (PDF)            │                             │
│  │  ├─ Tesseract    (Image OCR)      │                             │
│  │  ├─ crawl4ai     (URL Scraping)   │                             │
│  │  └─ Raw Text     (Direct Input)   │                             │
│  └───────────────────────────────────┘                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GOOGLE GEMINI 1.5 FLASH (LLM)                  │
│            Prompt → Generate → Validate → Return                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Flow:** Input → Extract → Prompt Construction → LLM Generation → Pydantic Validation → Structured JSON Response

---

## Tech Stack & Design Decisions

| Layer | Technology | Version | Why |
|---|---|---|---|
| **Runtime** | Python | 3.9 | Broad ecosystem support for AI/ML libraries; slim Docker images available |
| **Web Framework** | Flask | 3.0.3 | Lightweight, battle-tested for API-first services; minimal overhead for this scope |
| **LLM Orchestration** | LangChain | 0.3.9 | Standardized chain abstraction, output parsers, and model integration patterns |
| **LLM Provider** | Google Gemini 1.5 Flash | — | High throughput, low latency, generous free tier; sufficient for structured generation tasks |
| **Output Validation** | Pydantic | 2.10 | Schema enforcement at parse time; prevents malformed LLM output from reaching clients |
| **PDF Extraction** | PyPDF2 | 3.0.1 | Zero-dependency PDF text extraction; handles most standard PDF layouts |
| **Image OCR** | Tesseract + Pillow | 0.3.10 / 10.4 | Open-source OCR pipeline; no external API dependency for image-based input |
| **Web Scraping** | crawl4ai | 0.3.746 | Async headless crawling with markdown conversion; built-in anti-bot handling |
| **Frontend** | Tailwind CSS + Jinja2 | 2.2.19 | Utility-first styling with server-rendered templates; zero build step |
| **CORS** | flask-cors | 4.0.0 | Cross-origin support for decoupled frontend deployments (Vercel, local dev) |
| **Containerization** | Docker (multi-stage) | — | Reproducible builds; minimized runtime image via builder stage separation |
| **Deployment** | Render (API) + Vercel (Frontend) | — | Managed hosting with auto-deploy from Git; no infrastructure management overhead |

---

## Key Features & Production-Ready Standards

### Input Flexibility
- **PDF Upload** — Multi-page extraction via PyPDF2
- **Image OCR** — Text recognition from screenshots, photos, scanned documents
- **URL Scraping** — Async crawling with promotional content filtering and deduplication
- **Raw Text** — Direct paste for maximum control

### Pedagogical Configurability
- **Bloom's Taxonomy** — 6 levels (Remembering → Creating) with level-specific prompt engineering
- **Question Types** — MCQ, Fill-in-the-Blanks, True/False, One-Line Answers
- **Difficulty Levels** — Easy, Moderate, Hard with tiered complexity instructions

### Output Quality
- **Pydantic Schema Validation** — Every LLM response is parsed through `QuestionSet` model; malformed output is caught and retried via `OutputFixingParser`
- **Structured JSON** — Consistent schema: `question`, `options`, `answer`, `explanation`
- **Anti-Repetition** — Prompt-level instructions prevent duplicate questions within a single generation batch

### Security & Limits
- **CORS Whitelist** — Explicit origin allowlist; no wildcard `*`
- **File Size Cap** — 16 MB maximum upload (`MAX_CONTENT_LENGTH`)
- **Input Validation** — Empty input rejection before LLM call
- **API Key Management** — Environment variable injection; no hardcoded secrets in code (see note below)

### Architecture Decisions
- **Multi-stage Docker Build** — Builder stage installs dependencies and Playwright/Chromium; runtime stage copies only artifacts, reducing image size
- **Prompt Externalization** — Bloom's taxonomy, question types, and difficulty levels stored as JSON; no code changes required to add new configurations
- **Adapter Pattern** — Text extraction methods are isolated in `utils/text_extraction.py`; adding new input formats (e.g., video transcripts) requires zero changes to core logic

---

## Getting Started

### Prerequisites
- Python 3.9+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Docker (optional, for containerized setup)

### Option 1: Local Setup

```bash
# Clone the repository
git clone https://github.com/Assessli-tech/question-gen.git
cd question-gen

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_GENAI_API_KEY=your_api_key_here    # macOS/Linux
set GOOGLE_GENAI_API_KEY=your_api_key_here       # Windows

# Run the application
python app.py
```

The server starts at `http://localhost:5000`.

### Option 2: Docker

```bash
# Build the image
docker build -t question-generator .

# Run the container
docker run -p 5000:5000 -e GOOGLE_GENAI_API_KEY=your_api_key_here question-generator
```

### Option 3: Docker Compose (recommended for production-like setup)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GOOGLE_GENAI_API_KEY=${GOOGLE_GENAI_API_KEY}
    restart: unless-stopped
```

```bash
docker compose up --build
```

---

## Testing & Quality Assurance

### Run Locally

```bash
# Start the server
python app.py

# Test the health endpoint
curl http://localhost:5000/

# Test question generation
curl -X POST http://localhost:5000/generate \
  -F "bloom_level=Remembering" \
  -F "question_type=MCQ" \
  -F "difficulty_level=Easy" \
  -F "num_questions=5" \
  -F "context=DNA is a double-stranded molecule containing deoxyribose sugar."
```

### Expected Response

```json
{
  "questions": [
    {
      "question": "Which sugar is found in DNA?",
      "options": ["Ribose", "Deoxyribose", "Glucose", "Fructose"],
      "answer": "Deoxyribose",
      "explanation": "DNA contains deoxyribose sugar."
    }
  ]
}
```

### Linting & Static Analysis

```bash
# Install dev dependencies
pip install flake8 black mypy

# Lint
flake8 app.py models/ utils/

# Format
black app.py models/ utils/

# Type check
mypy app.py models/
```

### Prompt Validation

Prompt configurations are stored in `prompts/*.json`. Validate structure before deployment:

```bash
python -c "import json; [json.load(open(f)) for f in ['prompts/blooms.json', 'prompts/question_types.json', 'prompts/difficulty.json']]"
```

---

## CI/CD & Deployment

### Automated Pipeline

```
Push to main → Build Docker Image → Run Tests → Deploy
```

| Stage | Action |
|---|---|
| **Build** | Multi-stage Docker build with dependency caching |
| **Test** | Validate prompt JSON schemas, run lint checks, smoke-test `/generate` endpoint |
| **Deploy** | Render auto-deploys on push to `main`; frontend deploys to Vercel |

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_GENAI_API_KEY` | Yes | Google Gemini API key for LLM access |
| `PORT` | No | Server port (default: `5000`) |

### Production Considerations

- **Rate Limiting** — Add `flask-limiter` to throttle per-client LLM calls
- **Monitoring** — Integrate Sentry or Datadog for error tracking and latency metrics
- **Caching** — Cache frequent input→output pairs to reduce LLM costs
- **Async Workers** — Offload LLM calls to Celery/RQ for non-blocking request handling at scale

---

## Project Structure

```
question_generator_2.0/
├── app.py                          # Flask application entry point & route handlers
├── Dockerfile                      # Multi-stage Docker build
├── requirements.txt                # Python dependencies
├── models/
│   ├── langchain_gemini_model.py   # LLM orchestration (LangChain chains + Gemini)
│   └── pydantic_validators/
│       └── pydantic_model.py       # Output schema definitions
├── utils/
│   ├── text_extraction.py          # PDF, Image, URL text extraction adapters
│   └── web_scrap_processing.py     # Scraped content cleaning & deduplication
├── prompts/
│   ├── blooms.json                 # Bloom's Taxonomy level definitions
│   ├── question_types.json         # Question format specifications
│   └── difficulty.json             # Difficulty tier instructions
├── templates/
│   └── index.html                  # Jinja2 server-rendered UI
├── static/
│   └── js/main.js                  # Client-side form handling & rendering
└── PDF/                            # Sample test documents
```

---

## License

MIT
