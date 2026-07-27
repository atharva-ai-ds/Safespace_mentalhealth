# 💙 SafeSpace AI

An AI-powered Mental Health Assistant built using **FastAPI**, **LangGraph**, **Ollama**, and **Retrieval-Augmented Generation (RAG)**.

SafeSpace AI provides empathetic mental health support while delivering trusted information retrieved from verified mental health documents such as WHO guidelines.

---

## 🚀 Features

- 🧠 AI-powered Mental Health Assistant
- 📚 Retrieval-Augmented Generation (RAG)
- 📄 Uses trusted PDF knowledge base
- 💬 Conversational Memory
- ❤️ Empathetic Responses
- 🧭 Intent Classification
- ⚡ FastAPI Backend
- 🤖 Ollama Local LLM
- 🔍 Chroma Vector Database
- 🌐 Streamlit Chat Interface

---

## 🏗️ System Architecture

```
                User
                  │
                  ▼
        Streamlit Frontend
                  │
                  ▼
            FastAPI Backend
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  Intent Classifier      Conversation Memory
        │                   │
        └─────────┬─────────┘
                  ▼
             LangGraph Agent
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
        RAG              Ollama LLM
        │                   │
        ▼                   ▼
  Chroma Vector DB      Qwen Model
        │
        ▼
 Trusted Mental Health PDFs
```

---

## 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend

- FastAPI
- LangGraph
- LangChain

### AI Models

- Ollama
- Qwen
- Nomic Embeddings

### Vector Database

- ChromaDB

### Knowledge Base

- WHO Guidelines
- Anxiety
- Depression
- Stress
- Panic Disorder PDFs

---

## 📂 Project Structure

```
SafeSpace-RAG/

│
├── backend/
│   ├── ai_agent.py
│   ├── rag.py
│   ├── main.py
│   ├── tools.py
│   ├── memory.py
│   ├── prompts.py
│   ├── intent_classifier.py
│   └── config.py
│
├── frontend/
│   └── Frontend.py
│
├── documents/
│   ├── anxiety.pdf
│   ├── depression.pdf
│   ├── stress.pdf
│   ├── panic.pdf
│   └── who_guidelines.pdf
│
├── vector_db/
│
├── logs/
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/SafeSpace-AI.git

cd SafeSpace-AI
```

---

### Create Virtual Environment

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\Activate.ps1
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Install Ollama

Download Ollama from

https://ollama.com

---

### Pull Models

```bash
ollama pull qwen3:1.7b

ollama pull nomic-embed-text
```

---

### Build Vector Database

```bash
python -m backend.build_vector_db
```

---

### Start Backend

```bash
uvicorn backend.main:app --reload
```

---

### Start Frontend

```bash
streamlit run frontend/Frontend.py
```

---

## 📚 Knowledge Base

The chatbot retrieves information from trusted mental health documents including:

- WHO Mental Health Guidelines
- Depression
- Anxiety
- Stress
- Panic Disorder

---

## 💬 Example Questions

- What is anxiety?
- Symptoms of depression
- What is stress?
- How to reduce anxiety?
- What are panic attacks?
- How can I improve my mental health?

---

## 🔄 Workflow

1. User sends a message.
2. Intent Classifier identifies the request.
3. LangGraph orchestrates the workflow.
4. RAG retrieves relevant documents from ChromaDB.
5. Ollama generates a context-aware response.
6. Response is returned to the Streamlit interface.

---

## 📈 Future Improvements

- Voice Conversation
- PDF Upload Support
- Emotion Detection
- Crisis Risk Detection
- User Authentication
- Conversation Export
- Multilingual Support
- Cloud Deployment

---

## ⚠️ Disclaimer

SafeSpace AI provides educational mental health information and emotional support.

It is **not** a substitute for licensed psychologists, psychiatrists, therapists, or emergency medical services.

---

## 👨‍💻 Author

**Atharva Karanjkar**

AI & Data Science Engineer

CDAC PG-Diploma in Artificial Intelligence

GitHub: https://github.com/yourusername

LinkedIn: https://linkedin.com/in/yourprofile

---

## ⭐ If you found this project useful

Please consider giving it a ⭐ on GitHub.
