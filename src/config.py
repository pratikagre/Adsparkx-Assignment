import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL = "text-embedding-004"
LLM_MODEL = "gemini-2.5-flash"

SIMILARITY_THRESHOLD = 0.45

SENSITIVE_KEYWORDS = [
    "refund", "billing dispute", "overcharge", "double charge", 
    "unauthorized charge", "cancel account", "delete my account", 
    "close account", "sue", "legal", "lawyer", "attorney", 
    "breach of contract", "terms of service violation"
]

MAX_DISSATISFIED_TURNS = 3
