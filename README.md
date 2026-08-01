# Verified - AI-Powered Media Literacy & Misinformation Platform Backend

Verified is a backend application powered by FastAPI, SQLAlchemy, and LLMs designed to detect, extract, search, and verify health claims from user queries. It features robust multilingual claim extraction (with special support for Yoruba), a web-evidence retrieval engine using Tavily Search, and a reasoning system to evaluate claim veracity against medical literature.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Client Request] --> B[FastAPI Router]
    B --> C[Claim Extraction AI]
    C --> D[YarnGPT TTS Proxy]
    C --> E[Tavily Search API]
    E --> F[Evidence Reasoning Engine]
    F --> G[SQLAlchemy Database]
    B --> H[Community Library Board]
    H --> G
```

---

## 🛠️ Tech Stack

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
*   **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/) (Migrations)
*   **Database**: PostgreSQL (Supabase hosted)
*   **AI Services**:
    *   **LLM Integration**: Groq API Client (model: `openai/gpt-oss-20b`)
    *   **TTS Service**: YarnGPT API (`https://yarngpt.ai/`)
*   **Web Search**: Tavily Search API (for retrieving scientific/medical evidence)

---

## 📁 Repository Structure

```
├── alembic/              # Database migration environments and version history
├── ai/
│   ├── extraction.py     # Health claim extraction prompts and schemas
│   ├── llm.py            # Groq API client wrapper
│   └── reasoning.py      # Medical evidence analysis and verdict engine
├── config/
│   ├── base.py           # Database engine & session configuration
│   ├── dependencies.py   # FastAPI dependency injection (DB sessions)
│   └── settings.py       # Configuration settings parser (via python-decouple)
├── models/
│   └── library.py        # Library database model
├── routes/
│   ├── community.py      # Community board GET/POST/SEARCH routes
│   └── extraction.py     # Claim extraction, verification, and TTS proxy routes
├── .env                  # Environment secrets configuration (API keys, DB url)
├── main.py               # Main application entrypoint
└── README.md             # Project documentation
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your system.

### 2. Install Dependencies
Activate your virtual environment and install the required packages:
```bash
python -m venv .venv
# On Windows (cmd):
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary httpx python-decouple groq
```

### 3. Environment Variables Configuration
Create a `.env` file in the root directory:
```env
groq_api_key=your_groq_api_key
tavily_api_key=your_tavily_api_key
yarngpt_api_key=your_yarngpt_api_key
database_url=postgresql://username:password@host:port/database
```

---

## 🔌 API Endpoints

### 🩺 Verification Router (`/verify`)

#### **Extract & Verify Claim**
*   **Endpoint**: `POST /verify`
*   **Request Body**:
    ```json
    {
      "claim": "Drinking warm water daily cures malaria"
    }
    ```
*   **Behavior**: Extracts the core claim, automatically detects if the input is in Yoruba (`yo`) and handles translations, performs search queries on reputable medical domains (`cdc.gov`, `who.int`, `pubmed.ncbi.nlm.nih.gov`), runs reasoning on the evidence, and returns a verdict (`SUPPORTED`, `MISLEADING`, `CONTRADICTED`, etc.).

#### **Text-To-Speech (TTS) Proxy**
*   **Endpoint**: `POST /verify/tts`
*   **Request Body**:
    ```json
    {
      "text": "Correct medical advice to read out",
      "voice": "Idera"
    }
    ```
*   **Response**: Audio stream (`audio/mpeg`).

---

### 👥 Community Library Router (`/community`)

#### **Post Debunked Claim to Board**
*   **Endpoint**: `POST /community/post`
*   **Request Body**:
    ```json
    {
      "username": "user123",
      "debunked_claim": {
         "claim": "Warm water cures malaria",
         "verdict": "CONTRADICTED"
      }
    }
    ```

#### **Get All Claims**
*   **Endpoint**: `GET /community/get`

#### **Get Specific Claim**
*   **Endpoint**: `GET /community/get/{claim_id}`

#### **Search Community Board**
*   **Endpoint**: `GET /community/search?query=malaria`

---

## 🌍 Multilingual Support (Yoruba)

The pipeline is fully optimized to handle Yoruba inputs:
*   **Detection**: The extraction model outputs the original Yoruba query alongside its ISO 639-1 language code (`yo`).
*   **Translation**: Non-English inputs are automatically converted to English outputs by the reasoning engines where necessary to guarantee alignment with scientific sources.

---

## 🏃 Running the Application

Start the local development server:
```bash
uvicorn main:app --reload
```
Once running, you can access the interactive API docs at:
*   Swagger UI: http://127.0.0.1:8000/docs
*   ReDoc: http://127.0.0.1:8000/redoc
