import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.generator import generate_adaptive_response
from src.escalator import evaluate_escalation

load_dotenv()

test_scenarios = [
    {
        "id": 1,
        "query": "Where is the guide to clear cookies? It's been an hour and nothing is loading on your interface!",
        "desc": "Frustrated User: clear cookies / loading issue"
    },
    {
        "id": 2,
        "query": "What are the header parameter requirements for your bearer token auth implementation?",
        "desc": "Technical Expert: API auth details"
    },
    {
        "id": 3,
        "query": "Our operational uptime is decreasing. We need a timeline of when billing disputes are resolved.",
        "desc": "Business Executive: Billing timelines and operational impact"
    },
    {
        "id": 4,
        "query": "I'm experiencing an issue with your database integration that's causing internal errors.",
        "desc": "Technical Expert: Database integration error"
    },
    {
        "id": 5,
        "query": "My billing statement has unexpected duplicate charges. I demand an immediate refund!",
        "desc": "Frustrated User + Sensitive: Billing dispute requesting refund"
    },
    {
        "id": 6,
        "query": "How do I make a cake?",
        "desc": "Out-of-scope query (Should trigger low-confidence escalation)"
    }
]

def run_tests():
    print("=" * 60)
    print("STARTING TEST RUN FOR PERSONA-ADAPTIVE AGENT")
    print("=" * 60)

    print("Initializing RAG Pipeline and ingesting files...")
    rag = LocalRAGPipeline()
    
    kb_dir = Path("data")
    if not any(kb_dir.glob("*")):
        print("Knowledge base directory is empty. Run generate_kb.py first!")
        return
        
    rag.ingest_directory(kb_dir)
    print(f"Ingested documents. Total documents in DB collection: {rag.collection.count()}\n")

    history = []

    for scenario in test_scenarios:
        query = scenario["query"]
        print(f"\nScenario #{scenario['id']}: {scenario['desc']}")
        print(f"User Query: \"{query}\"")
        print("-" * 50)
        
        classification = classify_customer_persona(query)
        persona = classification.get("persona", "Frustrated User")
        sentiment = classification.get("sentiment", "Neutral")
        urgency = classification.get("urgency", "Medium")
        reasoning = classification.get("reasoning", "")
        
        print(f"Detected Persona: {persona}")
        print(f"Detected Sentiment: {sentiment}")
        print(f"Detected Urgency: {urgency}")
        print(f"Classification Reasoning: {reasoning}")
        
        context = rag.retrieve_context(query, top_k=2)
        print(f"Retrieved {len(context)} chunks:")
        for idx, chunk in enumerate(context):
            print(f"  [{idx+1}] Source: {chunk['source']} | Cosine Similarity Score: {chunk['score']}")
            print(f"      Snippet: {chunk['text'][:120]}...")
            
        escalation = evaluate_escalation(
            user_query=query,
            persona=persona,
            sentiment=sentiment,
            context_chunks=context,
            chat_history=history
        )
        
        if escalation["escalated"]:
            print("\n>>> ESCALATION TRIGGERED!")
            print(f"Reason: {escalation['reason']}")
            print("Structured Human Handoff JSON:")
            print(json.dumps(escalation["handoff_summary"], indent=2))
            
            history.append({
                "role": "user",
                "text": query,
                "sentiment": sentiment,
                "persona": persona
            })
            history.append({
                "role": "assistant",
                "response": "ESCALATED TO HUMAN: " + escalation["reason"],
                "escalated": True
            })
        else:
            print("\n>>> RESPONSE GENERATION...")
            response = generate_adaptive_response(query, persona, context)
            print(f"Generated Response ({persona} style):\n{response}")
            
            history.append({
                "role": "user",
                "text": query,
                "sentiment": sentiment,
                "persona": persona
            })
            history.append({
                "role": "assistant",
                "response": response,
                "escalated": False
            })
            
        print("=" * 60)

if __name__ == "__main__":
    run_tests()
