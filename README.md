# Persona-Adaptive Customer Support Agent

An intelligent, persona-aware customer support agent built with Python, Gemini, ChromaDB, and Streamlit. The agent automatically detects customer communication archetypes, retrieves context from a local vector knowledge base (RAG), adapts its response tone accordingly, and triggers an automated escalation workflow (compiling a structured JSON handoff) when appropriate.

---

## 1. Project Overview

Customer support demands different approaches depending on who is asking. A software engineer wants granular logs and code blocks, a frustrated user needs empathy and simple instructions, and an executive needs a concise business impact summary. This application addresses these requirements by orchestrating:
1. **Persona Detection**: Uses Gemini to classify customer queries into three distinct archetypes: `Technical Expert`, `Frustrated User`, and `Business Executive`.
2. **RAG Pipeline**: Leverages ChromaDB and Gemini's `text-embedding-004` model to index local support documentation (including PDFs, markdown, and text files) and retrieve relevant troubleshooting guides.
3. **Persona-Adaptive Generation**: Selects custom system prompts dynamically to match the response style of the detected persona.
4. **Escalation & Handoff**: Triggers human handoff when information is missing, when confidence is low, when billing/account deletion sensitivity is detected, or when consecutive interactions indicate persistent frustration.

---

## 2. Architecture Diagram

```
                 [ User Query ]
                       │
                       ▼
             ┌───────────────────┐
             │ Persona & Sentiment│
             │     Classifier    │
             └───────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
    [Persona Tag]       [Sentiment Tag]
    - Tech Expert       - Positive
    - Frustrated User   - Neutral
    - Business Exec     - Angry/Frustrated
             │                   │
             ▼                   │
    ┌───────────────────┐        │
    │  Semantic Search  │        │
    │    (ChromaDB)     │        │
    └───────────────────┘        │
             │                   │
             ▼                   │
    ┌───────────────────┐        │
    │  Escalation Check │◄───────┘
    │  (Confidence,     │
    │  Keywords,        │
    │  Frustration)     │
    └─────────┬─────────┘
              │
      ┌───────┴────────────────────────┐
      │ (Pass)                         │ (Fail / Sensitive)
      ▼                                ▼
┌──────────────────────────┐    ┌────────────────────────┐
│ Persona-Adaptive Prompt  │    │  Human Agent Escalation│
│        Generator         │    │       Workflow         │
└──────────────────────────┘    └────────────────────────┘
      │                                │
      ▼                                ▼
[Adaptive Response Text]        [Structured Handoff JSON]
```

---

## 3. Tech Stack

- **Language**: Python 3.12+
- **Core LLM & Embeddings**: `google-genai` (utilizing `gemini-2.5-flash` and `text-embedding-004`)
- **Vector Database**: `chromadb` (v0.4+)
- **Text Chunking & Splitting**: `langchain-text-splitters`
- **PDF Parser**: `pypdf`
- **Frontend UI & Visualization**: `streamlit` (v1.30+)
- **Data Operations**: `pandas`
- **Configuration & Environment**: `python-dotenv`
- **PDF Document Compiler**: `reportlab` (for programmatically building test documents)

---

## 4. Persona Detection Strategy

The classification engine inside `src/classifier.py` runs a zero-shot structured text analysis on user queries using Gemini's structured JSON output capability.

### 1. Classification Method
We enforce a strict JSON Schema definition on the Gemini API output, forcing the model to return exactly four keys: `persona`, `sentiment`, `urgency`, and `reasoning`.

### 2. Classification Rules
- **Technical Expert**: Uses developer terminology (e.g., *API*, *bearer token*, *401 Unauthorized*, *Postgres connection*, *header parameter*). Requests code, configuration details, or logs.
- **Frustrated User**: Uses emotional keywords (e.g., *broken*, *worst*, *useless*, *nothing works*), uppercase text, or exclamation marks. Expresses high urgency or complaints.
- **Business Executive**: Focuses on business metrics, operational downtime, refund requests, timelines, and business operations. Prefers short, outcome-driven answers.

---

## 5. RAG Pipeline Design

The system relies on a local Retrieval-Augmented Generation pipeline built in `src/rag_pipeline.py`.

- **Chunking Strategy**: Documents are parsed (PDFs page-by-page via `pypdf`, text and markdown natively) and split using `RecursiveCharacterTextSplitter`. We use a chunk size of **500 characters** with an overlap of **50 characters** to ensure that technical credentials and steps are not split across chunks.
- **Embedding Model**: Text chunks are embedded using Gemini's state-of-the-art `text-embedding-004` model, which generates 768-dimensional vector representations capturing semantic meaning.
- **Vector Database**: We utilize **ChromaDB** configured to run locally (`./chroma_db`) and use the **Cosine Similarity** space (`"hnsw:space": "cosine"`).
- **Retrieval & Scoring**: When a query is submitted, it is embedded and matched against document vectors. The cosine distance is translated into a simulated confidence score:
  $$\text{Similarity Score} = 1.0 - \text{Cosine Distance}$$

---

## 6. Escalation Logic & Triggers

The system automatically halts chatbot execution and generates a human agent handoff in `src/escalator.py` when any of the following conditions are met:

1. **Low Retrieval Confidence**: The top retrieved document chunk has a Cosine Similarity score below **0.45**, indicating that the knowledge base does not contain enough information to resolve the issue.
2. **Sensitive Support Topics**: The query contains sensitive keywords such as refund requests, account cancellation, account deletion, or legal threats.
3. **Explicit Agent Request**: The customer uses phrases like "talk to support", "speak to human", or "live agent".
4. **Persistent Dissatisfaction**: The customer remains in an "Angry/Frustrated" sentiment for **3 consecutive turns** during a single session.

### Structured Handoff Example
```json
{
  "persona": "Frustrated User",
  "sentiment": "Angry/Frustrated",
  "detected_issue": "My billing statement has unexpected duplicate charges. I demand an immediate refund!",
  "escalation_reasons": [
    "Sensitive keyword detected: 'refund'"
  ],
  "documents_used": [
    "billing_policy.md"
  ],
  "attempted_steps": [],
  "best_retrieved_confidence": 0.54,
  "recommended_next_steps": "Verify customer invoice history and initiate billing refund/adjustment verification in Stripe admin."
}
```

---

## 7. Setup & Installation Instructions

Follow these steps to run the application locally on your Windows system.

### Step 1: Clone and Navigate
Navigate to the directory in your shell:
```powershell
cd "c:\Users\agrep\OneDrive\Desktop\Adsparkx Assignment"
```

### Step 2: Setup Environment and Virtual Env
Create a Python virtual environment:
```powershell
python -m venv venv
```
Activate the environment:
```powershell
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure API Credentials
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

### Step 5: Ingest Support Documents
Generate the standard knowledge base articles (including compiling ReportLab PDF):
```powershell
python scratch/generate_kb.py
```
Ingest the documents into the local Chroma vector database:
```powershell
python src/rag_pipeline.py
```

### Step 6: Launch Web Interface
```powershell
streamlit run app.py
```

---

## 8. Verification and Test Queries

The application is validated against the following five scenarios:

1. **Frustrated User (Cookies / Loading)**
   - *Query*: "Where is the guide to clear cookies? It's been an hour and nothing is loading on your interface!"
   - *Behavior*: Empathic validation, simple troubleshooting, bullet list.
2. **Technical Expert (Bearer Token Headers)**
   - *Query*: "What are the header parameter requirements for your bearer token auth implementation?"
   - *Behavior*: Returns precise header strings (`Authorization: Bearer <YOUR_API_KEY>`) and code examples.
3. **Business Executive (Downtime Timeline)**
   - *Query*: "Our operational uptime is decreasing. We need a timeline of when billing disputes are resolved."
   - *Behavior*: Returns a brief summary of billing resolution times (2-3 business days) without technical jargon.
4. **Technical Expert (Database Connect)**
   - *Query*: "I'm experiencing an issue with your database integration that's causing internal errors."
   - *Behavior*: Retrieves db integration parameters, whitelists, and SSL requirement instructions.
5. **Sensitive Billing Escalation**
   - *Query*: "My billing statement has unexpected duplicate charges. I demand an immediate refund!"
   - *Behavior*: Bypasses standard generation, triggers immediate billing escalation, and shows human handoff JSON.

---

## 9. Known Limitations & Future Improvements

- **Local Storage Limitations**: ChromaDB is running locally in SQLite mode; in production workloads, this would be hosted in a remote instance (e.g. Qdrant or Pinecone) for multi-tenant scalability.
- **Sentiment State Persistence**: The consecutive anger threshold is tracked per-session in Streamlit memory; production systems should store conversation state in a persistent DB (e.g., Redis or PostgreSQL) to survive application restarts.
- **Multilingual Support**: Currently optimized for English; adding translation/multilingual models would allow persona-adaptive support in different languages.
