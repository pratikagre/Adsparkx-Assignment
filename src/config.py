import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# RAG Configuration
EMBEDDING_MODEL = "text-embedding-004"
LLM_MODEL = "gemini-2.5-flash"  # Standard high-speed Gemini model

# Confidence threshold for similarity score (Cosine Similarity)
# Distance in Chroma for cosine is: 1 - cosine_similarity.
# So cosine_similarity = 1 - distance.
SIMILARITY_THRESHOLD = 0.45

# Escalation Configuration
SENSITIVE_KEYWORDS = [
    "refund", "billing dispute", "overcharge", "double charge", 
    "unauthorized charge", "cancel account", "delete my account", 
    "close account", "sue", "legal", "lawyer", "attorney", 
    "breach of contract", "terms of service violation"
]

# Max interactions before automated escalation due to persistent dissatisfaction
MAX_DISSATISFIED_TURNS = 3
