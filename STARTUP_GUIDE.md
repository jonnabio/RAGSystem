# 🚀 RAG System - Complete Full-Stack Application

**Status**: ✅ **READY TO RUN!**

A stunning AI-powered document Q&A system with:

- **Beautiful UI**: Dark blue × Fiserv orange design with glassmorphism
- **Multi-Model LLMs**: GPT-4, Claude, Llama 3, and more via OpenRouter
- **Smart RAG**: Vector search with LanceDB
- **Full-Stack**: FastAPI backend + Next.js frontend

---

## 📋 Prerequisites

Before running, you need API keys:

1. **OpenRouter API Key** (for LLMs)
   - Get free key at: https://openrouter.ai/
   - Free models available (Llama 3, Mistral, etc.)

2. **OpenAI API Key** (for embeddings)
   - Get key at: https://platform.openai.com/api-keys
   - Used only for text embeddings (~$0.0001 per 1K tokens)

---

## ⚙️ Setup (One-Time)

### 1. Configure Backend

Edit `backend/.env` and add your API keys:

```bash
# REQUIRED: Add your actual keys here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

### 2. Install Dependencies (if not done)

```bash
# Backend
cd backend
python -m venv venv
.\\venv\\Scripts\\Activate.ps1  # Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

---

## 🏃 Running the Application

### Open 2 Terminal Windows

**Terminal 1 - Backend (FastAPI)**

```bash
cd backend
.\\venv\\Scripts\\Activate.ps1
python src/main.py
```

✅ Backend will start at: **http://localhost:8001**

- API Docs (Swagger): http://localhost:8001/docs
- Health Check: http://localhost:8001/health

**Terminal 2 - Frontend (Next.js)**

```bash
cd frontend
npm run dev
```

✅ Frontend will start at: **http://localhost:3000**

---

## 🎨 Using the Application

### 1. Open the Dashboard

Visit: **http://localhost:3000**

You'll see:

- Beautiful gradient hero section
- Stats cards (Documents, Queries, Tokens)
- Quick action buttons

### 2. Upload Documents

1. Click "Upload Documents" or go to http://localhost:3000/documents
2. Drag & drop a PDF or DOCX file (or click to browse)
3. Watch the progress bar as it processes
4. Document will show "✓ Processed" when ready

### 3. Start Chatting

1. Click "Start Chat" or go to http://localhost:3000/chat
2. Select your preferred model (Llama 3 is free!)
3. Type your question about the uploaded documents
4. Get intelligent answers with:
   - Source citations
   - Confidence scores
   - Token usage
   - Cost tracking

---

## ✨ Features Implemented

### Backend (FastAPI)

- ✅ Document upload (PDF, DOCX)
- ✅ Text extraction with PyMuPDF & python-docx
- ✅ Smart chunking with overlap
- ✅ OpenAI embeddings (3072 dimensions)
- ✅ LanceDB vector storage
- ✅ RAG query pipeline
- ✅ OpenRouter multi-model support
- ✅ CORS enabled for frontend
- ✅ Swagger API docs

### Frontend (Next.js)

- ✅ Stunning dark blue × Fiserv orange UI
- ✅ Glassmorphism effects
- ✅ Smooth animations
- ✅ Responsive design
- ✅ Dashboard with stats
- ✅ Chat interface with history
- ✅ Document management with drag-and-drop
- ✅ Model selector
- ✅ Confidence badges
- ✅ Source citations
- ✅ Real-time status indicators

---

## 🧪 Testing the System

### Quick Test Flow

1. **Upload a document**:
   - Go to Documents page
   - Upload a PDF (try a research paper or report)
   - Wait for "✓ Processed" status

2. **Ask questions**:
   - Go to Chat page
   - Example queries:
     - "What is this document about?"
     - "Summarize the main findings"
     - "What are the key conclusions?"

3. **Check sources**:
   - Each answer shows source documents
   - Confidence score indicates quality
   - Token usage shown for transparency

### API Testing (Swagger)

Visit: http://localhost:8000/docs

Try endpoints directly:

- `POST /api/documents/upload` - Upload files
- `GET /api/documents` - List documents
- `POST /api/chat` - Ask questions
- `GET /api/models` - List available models

---

## 🎯 Available LLM Models

### Free Models (via OpenRouter)

- **Llama 3 70B** - Fast, high quality
- **Mistral Medium** - Great for general use
- **Gemma 7B** - Efficient, fast

### Paid Models

- **GPT-4 Turbo** - Best quality (~$0.01/1K tokens)
- **Claude 3 Opus** - Excellent reasoning (~$0.015/1K tokens)
- **Gemini Pro** - Google's model (~$0.0005/1K tokens)

---

## 📁 Project Structure

```
RAGSystem/
├── backend/
│   ├── src/
│   │   ├── features/          # Domain-driven modules
│   │   │   ├── chat/          # Chat service
│   │   │   ├── documents/     # Document processing
│   │   │   ├── rag/           # RAG pipeline
│   │   │   └── analytics/     # Analytics (future)
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Unit tests
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Dashboard
│   │   ├── chat/              # Chat interface
│   │   ├── documents/         # Document management
│   │   └── globals.css        # Design system
│   └── package.json
└── data/
    ├── documents/             # Uploaded files
    ├── vectors/               # LanceDB database
    └── logs/                  # Application logs
```

---

## 🔧 Troubleshooting

### Backend won't start

- ✅ Check `.env` file has valid API keys
- ✅ Ensure virtual environment is activated
- ✅ Verify port 8001 is not in use

### Frontend won't start

- ✅ Run `npm install` in frontend directory
- ✅ Verify port 3000 is not in use
- ✅ Check `.env.local` exists

### API connection fails

- ✅ Backend must be running first
- ✅ Check console for CORS errors
- ✅ Verify URLs match (localhost:8001 and localhost:3000)

### Document upload fails

- ✅ Check file is PDF or DOCX
- ✅ Ensure file size < 10MB
- ✅ Verify backend is processing (check terminal logs)

### No answers from chat

- ✅ Upload documents first!
- ✅ Check valid API keys in backend/.env
- ✅ Try simpler questions initially
- ✅ Check backend logs for errors

---

## 💡 Tips for Best Results

### Document Upload

- Use clear, well-formatted PDFs
- Avoid scanned images (no OCR yet)
- Single-topic documents work best

### Asking Questions

- Be specific about what you want
- Reference document topics
- Try follow-up questions
- Check confidence scores

### Model Selection

- Start with free models (Llama 3)
- Use GPT-4 for complex reasoning
- Claude 3 for long documents
- Gemini Pro for speed

---

## 🌟 What's Implemented

### Phase 1 Complete (100%)

- ✅ Full backend with RAG pipeline
- ✅ Beautiful responsive UI
- ✅ Document upload & processing
- ✅ Multi-model chat
- ✅ Source citations
- ✅ Confidence scoring
- ✅ Cost tracking

### Future Enhancements (Phase 2)

- [ ] User authentication
- [ ] Document collections
- [ ] Advanced analytics dashboard
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] Export conversations
- [ ] Document annotations

---

## 📊 Architecture

### Backend Tech Stack

- **Framework**: FastAPI (async Python)
- **Vector DB**: LanceDB (local, serverless)
- **LLMs**: OpenRouter (multi-model)
- **Embeddings**: OpenAI text-embedding-3-large
- **Document Processing**: PyMuPDF, python-docx
- **Validation**: Pydantic v2

### Frontend Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Fonts**: Inter (Google Fonts)
- **Icons**: Unicode emoji (no dependencies!)

---

## 🎨 Design System

### Colors

- **Primary**: Dark Blue (#0a0e1a)
- **Accent**: Fiserv Orange (#ff6600)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Error**: Red (#ef4444)

### Effects

- Glassmorphism
- Gradient backgrounds
- Smooth transitions (300ms)
- Hover effects
- Loading states

---

## 📝 Development Notes

### Code Quality

- ✅ Type hints everywhere
- ✅ Comprehensive error handling
- ✅ Structured logging
- ✅ Modular architecture
- ✅ No secrets in code

### Testing

- ✅ Unit tests for domain layer
- ⏳ Integration tests (partial)
- ⏳ E2E tests (planned)

### Documentation

- ✅ README.md
- ✅ API documentation (Swagger)
- ✅ Inline docstrings
- ✅ ADRs for key decisions

---

## 🚀 Next Steps

1. **Add your API keys** to `backend/.env`
2. **Start both servers** (backend + frontend)
3. **Upload a document**
4. **Start asking questions!**

Enjoy your premium RAG System! 🎉

---

**Need Help?**

- Backend logs: Check terminal running `python src/main.py`
- Frontend logs: Check browser console (F12)
- API docs: http://localhost:8001/docs

**Built with ACE Framework v2.1**
