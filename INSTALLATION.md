# Installation

## Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js (for the frontend)
- [Ollama](https://ollama.com)

## 1. Pull the required local models
ollama pull qwen2.5-coder:7b-instruct-q4_0
ollama pull deepseek-r1:8b

Start Ollama's server (keep this running in its own terminal):
ollama serve
If you hit a `CPU_REPACK buffer` memory error on startup, set:
$env:OLLAMA_NOREPACK = "1"
ollama serve


## 2. Start the sandbox + policy engine
docker-compose up -d
Initialize DVWA: open `http://localhost:8080`, log in (`admin`/`password`), click **Create/Reset Database**, set **DVWA Security** to **Low**.

## 3. Install Python dependencies
Each module has its own `requirements.txt`:
pip install -r red-agent/requirements.txt --break-system-packages
pip install -r blue-agent/requirements.txt --break-system-packages
pip install -r governor/requirements.txt --break-system-packages
pip install -r pattern-auditor/requirements.txt --break-system-packages
pip install -r backend/requirements.txt --break-system-packages


## 4. Set environment variables
Create a `.env` file in `backend/`:
THRESHOLDGUARD_API_KEY=your-own-secret-key-here
Generate a random key if needed:
python -c "import secrets; print(secrets.token_hex(32))"


## 5. Run the backend
cd backend
uvicorn main:app --reload --port 8000

Visit `http://localhost:8000/docs` for the interactive API.

## 6. Run the frontend
cd frontend
npm install
npm run dev
Open the printed localhost URL. Update `API_KEY` in `frontend/src/components/Dashboard.jsx` to match your backend's `.env` value.
