import os
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).resolve().parent))

from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.generator import generate_adaptive_response
from src.escalator import evaluate_escalation
import src.config as config

st.set_page_config(
    page_title="Adsparkx Persona-Adaptive Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Styling elements */
    .stApp {
        background: linear-gradient(135deg, #3b0712 0%, #2f1205 50%, #3b0726 100%);
        color: #f1f5f9;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #f87171, #fb923c, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Persona Card Badges */
    .badge {
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .persona-tech {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    .persona-frustrated {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .persona-exec {
        background-color: rgba(168, 85, 247, 0.2);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.4);
    }
    
    .sentiment-positive {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    .sentiment-neutral {
        background-color: rgba(100, 116, 139, 0.2);
        color: #94a3b8;
        border: 1px solid rgba(100, 116, 139, 0.4);
    }
    .sentiment-angry {
        background-color: rgba(249, 115, 22, 0.2);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.4);
    }
    
    .urgency-high {
        background-color: rgba(220, 38, 38, 0.3);
        color: #ef4444;
        border: 1px solid #ef4444;
        animation: pulse 2s infinite;
    }
    .urgency-medium {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .urgency-low {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    @keyframes pulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }

    /* Source Box */
    .source-card {
        background-color: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Sidebar stats container */
    .stat-container {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "stats" not in st.session_state:
    st.session_state.stats = {
        "Technical Expert": 0,
        "Frustrated User": 0,
        "Business Executive": 0,
        "Positive": 0,
        "Neutral": 0,
        "Angry/Frustrated": 0,
        "total_queries": 0,
        "escalations": 0,
        "confidence_scores": []
    }

@st.cache_resource
def get_rag_pipeline():
    pipeline = LocalRAGPipeline()
    kb_dir = Path(__file__).resolve().parent / "data"
    
    if not kb_dir.exists() or not any(kb_dir.glob("*")):
        kb_dir.mkdir(parents=True, exist_ok=True)
        with open(kb_dir / "notice.md", "w") as f:
            f.write("# Knowledge Base Empty\n\nPlease add documents to /data directory and reindex.")
            
    if pipeline.collection.count() == 0 and any(kb_dir.glob("*")):
        pipeline.ingest_directory(kb_dir)
        
    return pipeline

try:
    rag_pipeline = get_rag_pipeline()
except Exception as e:
    st.error(f"Failed to initialize RAG pipeline: {e}")
    rag_pipeline = None

with st.sidebar:
    st.image("https://img.icons8.com/color/96/serverless.png", width=64)
    st.title("Adsparkx Support Panel")
    st.markdown("---")
    
    st.subheader("⚙️ Config settings")
    similarity_thresh = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=config.SIMILARITY_THRESHOLD,
        step=0.05,
        help="Minimum cosine similarity required to trust retrieved documents. Queries below this will automatically escalate."
    )
    
    config.SIMILARITY_THRESHOLD = similarity_thresh
    
    st.markdown("---")
    
    st.subheader("🗃️ Knowledge Base Index")
    doc_count = rag_pipeline.collection.count() if rag_pipeline else 0
    st.metric("Total Knowledge Chunks", doc_count)
    
    if st.button("🔄 Reindex Knowledge Base"):
        with st.spinner("Reindexing support documents from data/..."):
            kb_dir = Path(__file__).resolve().parent / "data"
            rag_pipeline.ingest_directory(kb_dir)
            st.success("Reindexing Complete!")
            st.rerun()
            
    st.markdown("---")

    st.subheader("📊 Session Analytics")
    stats = st.session_state.stats
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", stats["total_queries"])
    with col2:
        esc_rate = (stats["escalations"] / stats["total_queries"] * 100) if stats["total_queries"] > 0 else 0.0
        st.metric("Escalation Rate", f"{esc_rate:.1f}%")
        
    avg_conf = (sum(stats["confidence_scores"]) / len(stats["confidence_scores"])) if stats["confidence_scores"] else 0.0
    st.metric("Avg Doc Confidence", f"{avg_conf:.2f}")

    st.markdown("**User Personas Distribution**")
    if stats["total_queries"] > 0:
        persona_data = {
            "Persona": ["Tech Expert", "Frustrated", "Executive"],
            "Count": [stats["Technical Expert"], stats["Frustrated User"], stats["Business Executive"]]
        }
        df_p = pd.DataFrame(persona_data)
        st.bar_chart(df_p, x="Persona", y="Count", height=150)
    else:
        st.caption("No queries recorded yet.")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()


st.markdown("<div class='main-header'>Adsparkx Support Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Persona-Adaptive Customer Support Agent powered by Gemini RAG</div>", unsafe_allow_html=True)

for index, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    
    if role == "user":
        with st.chat_message("user"):
            st.write(msg["text"])
            
            persona = msg.get("persona")
            sentiment = msg.get("sentiment")
            urgency = msg.get("urgency")
            
            p_class = "persona-tech" if persona == "Technical Expert" else "persona-frustrated" if persona == "Frustrated User" else "persona-exec"
            s_class = "sentiment-positive" if sentiment == "Positive" else "sentiment-neutral" if sentiment == "Neutral" else "sentiment-angry"
            u_class = "urgency-high" if urgency == "High" else "urgency-medium" if urgency == "Medium" else "urgency-low"
            
            st.markdown(
                f"<span class='badge {p_class}'>Persona: {persona}</span>"
                f"<span class='badge {s_class}'>Sentiment: {sentiment}</span>"
                f"<span class='badge {u_class}'>Urgency: {urgency}</span>",
                unsafe_allow_html=True
            )
            if msg.get("reasoning"):
                with st.expander("🔍 Classification Justification"):
                    st.caption(msg["reasoning"])
                    
    elif role == "assistant":
        with st.chat_message("assistant", avatar="🛡️"):
            if msg.get("escalated"):
                st.error("🚨 **Ticket Escalated to Human Support**")
                st.write(msg["response"])
                
                if msg.get("handoff"):
                    st.markdown("### 📋 Structured Human Handoff Payload")
                    st.json(msg["handoff"])
            else:
                st.write(msg["response"])
                
                sources = msg.get("sources", [])
                if sources:
                    with st.expander("📚 Retrieved Knowledge Sources"):
                        for s_idx, src in enumerate(sources):
                            st.markdown(
                                f"<div class='source-card'>"
                                f"<b>[{s_idx+1}] File:</b> {src['source']} | "
                                f"<b>Similarity Match:</b> {src['score']:.4f}<br/>"
                                f"<i>\"{src['text']}\"</i>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                
                feedback_key = f"feedback_{index}"
                if msg.get("feedback"):
                    st.caption(f"Thank you for your feedback! (Marked as: {msg['feedback']})")
                else:
                    f_col1, f_col2, _ = st.columns([0.1, 0.1, 0.8])
                    with f_col1:
                        if st.button("👍", key=f"up_{index}"):
                            st.session_state.messages[index]["feedback"] = "helpful"
                            st.rerun()
                    with f_col2:
                        if st.button("👎", key=f"down_{index}"):
                            st.session_state.messages[index]["feedback"] = "unhelpful"
                            st.rerun()


user_query = st.chat_input("Describe your issue (e.g. API failures, billing disputes, password resets)...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)
    
    history_list_for_eval = []
    chat_history_str = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_history_str += f"Customer: {msg['text']}\n"
            history_list_for_eval.append({
                "role": "user",
                "text": msg["text"],
                "sentiment": msg.get("sentiment", "Neutral"),
                "persona": msg.get("persona", "Frustrated User")
            })
        else:
            chat_history_str += f"Agent: {msg['response']}\n"
            history_list_for_eval.append({
                "role": "assistant",
                "response": msg["response"],
                "escalated": msg.get("escalated", False)
            })

    with st.spinner("Analyzing message footprint..."):
        classification = classify_customer_persona(user_query, chat_history=chat_history_str)
        persona = classification.get("persona", "Frustrated User")
        sentiment = classification.get("sentiment", "Neutral")
        urgency = classification.get("urgency", "Medium")
        reasoning = classification.get("reasoning", "")

    st.session_state.messages.append({
        "role": "user",
        "text": user_query,
        "persona": persona,
        "sentiment": sentiment,
        "urgency": urgency,
        "reasoning": reasoning
    })

    st.session_state.stats["total_queries"] += 1
    st.session_state.stats[persona] += 1
    st.session_state.stats[sentiment] += 1

    with st.spinner("Searching knowledge base..."):
        if rag_pipeline:
            context = rag_pipeline.retrieve_context(user_query, top_k=2)
        else:
            context = []

    if context:
        best_score = max([c["score"] for c in context])
        st.session_state.stats["confidence_scores"].append(best_score)
    else:
        st.session_state.stats["confidence_scores"].append(0.0)

    with st.spinner("Evaluating compliance and satisfaction..."):
        escalation_result = evaluate_escalation(
            user_query=user_query,
            persona=persona,
            sentiment=sentiment,
            context_chunks=context,
            chat_history=history_list_for_eval
        )

    if escalation_result["escalated"]:
        st.session_state.stats["escalations"] += 1
        
        response_text = (
            "I apologize, but this request requires verification from our customer success teams. "
            "I have compiled your details and transferred your query to a live human representative who will respond shortly."
        )
        
        st.session_state.messages.append({
            "role": "assistant",
            "response": response_text,
            "escalated": True,
            "handoff": escalation_result["handoff_summary"]
        })
    else:
        with st.spinner("Generating persona-adaptive response..."):
            response_text = generate_adaptive_response(
                user_query=user_query,
                persona=persona,
                context_chunks=context,
                chat_history=chat_history_str
            )
            
        st.session_state.messages.append({
            "role": "assistant",
            "response": response_text,
            "escalated": False,
            "sources": context,
            "feedback": None
        })

    st.rerun()
