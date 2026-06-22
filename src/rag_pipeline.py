import os
from pathlib import Path
from google import genai
from google.genai import types
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from dotenv import load_dotenv

import src.config as config

load_dotenv()

class LocalRAGPipeline:
    def __init__(self, db_dir=None):
        self.db_dir = db_dir or config.CHROMA_DIR
        self.chroma_client = chromadb.PersistentClient(path=str(self.db_dir))
        self.collection = self.chroma_client.get_or_create_collection(
            name="support_kb",
            metadata={"hnsw:space": "cosine"}
        )
        self._init_genai_client()

    def _init_genai_client(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            self.genai_client = genai.Client(api_key=api_key)
        else:
            self.genai_client = genai.Client()

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of texts using text-embedding-004."""
        if not texts:
            return []
        try:
            response = self.genai_client.models.embed_content(
                model=config.EMBEDDING_MODEL,
                contents=texts
            )
            return [embedding.values for embedding in response.embeddings]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return [[0.0] * 768 for _ in texts]

    def get_embedding(self, text: str) -> list[float]:
        """Generates embedding for a single text chunk."""
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * 768

    def parse_document(self, file_path: Path) -> str:
        """Parses PDF, Markdown, and text files to extract raw string content."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            reader = PdfReader(file_path)
            content = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    content.append(text)
            return "\n\n".join(content)
        elif suffix in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def ingest_directory(self, directory_path: Path):
        """Iterates over a directory, parses files, splits into chunks, and adds to ChromaDB."""
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            print(f"Directory {directory_path} does not exist.")
            return

        supported_suffixes = [".pdf", ".txt", ".md"]
        files = [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in supported_suffixes]

        print(f"Found {len(files)} files to ingest.")
        
        self.chroma_client.delete_collection("support_kb")
        self.collection = self.chroma_client.get_or_create_collection(
            name="support_kb",
            metadata={"hnsw:space": "cosine"}
        )

        for file_path in files:
            try:
                print(f"Processing {file_path.name}...")
                content = self.parse_document(file_path)
                
                splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                chunks = splitter.split_text(content)
                
                if not chunks:
                    continue

                batch_size = 20
                for i in range(0, len(chunks), batch_size):
                    batch_chunks = chunks[i:i+batch_size]
                    batch_embeddings = self.get_embeddings(batch_chunks)
                    
                    ids = [f"{file_path.name}_chunk_{idx}" for idx in range(i, i + len(batch_chunks))]
                    metadatas = [{"source": file_path.name, "chunk_index": idx} for idx in range(i, i + len(batch_chunks))]
                    
                    self.collection.add(
                        ids=ids,
                        embeddings=batch_embeddings,
                        metadatas=metadatas,
                        documents=batch_chunks
                    )
                print(f"Successfully ingested {len(chunks)} chunks from {file_path.name}.")
            except Exception as e:
                print(f"Failed to ingest document {file_path.name}: {e}")

    def retrieve_context(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Performs semantic cosine similarity search in ChromaDB.
        Returns a list of dictionaries with text, source, and similarity score.
        """
        if self.collection.count() == 0:
            return []
            
        query_vector = self.get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        
        retrieved_items = []
        if results and results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                similarity_score = 1.0 - distance
                
                retrieved_items.append({
                    "text": results['documents'][0][i],
                    "source": results['metadatas'][0][i]['source'],
                    "score": round(similarity_score, 4)
                })
        return retrieved_items

if __name__ == "__main__":
    print("Testing pipeline initialization...")
    pipeline = LocalRAGPipeline()
    print("Collection count:", pipeline.collection.count())
