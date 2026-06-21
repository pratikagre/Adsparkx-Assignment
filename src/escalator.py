import json
import re
import src.config as config

def evaluate_escalation(
    user_query: str, 
    persona: str,
    sentiment: str,
    context_chunks: list[dict],
    chat_history: list[dict],
    manual_trigger: bool = False
) -> dict:
    """
    Evaluates whether the support request needs to be escalated to a human agent.
    Returns a dictionary:
    {
        "escalated": bool,
        "reason": str or None,
        "handoff_summary": dict or None
    }
    """
    reasons = []

    # 1. Manual User Trigger
    if manual_trigger:
        reasons.append("User requested human agent.")

    # 2. Check for Explicit Helpdesk/Human Agent request
    agent_keywords = [r"\bhuman\b", r"\blive agent\b", r"\blive support\b", r"\brepresentative\b", r"\bescalate\b", r"\btalk to a person\b"]
    for keyword in agent_keywords:
        if re.search(keyword, user_query.lower()):
            reasons.append("Explicit request for human support.")
            break

    # 3. Check for Sensitive Keywords (Billing, Account Deletion, Legal)
    for kw in config.SENSITIVE_KEYWORDS:
        if kw.lower() in user_query.lower():
            reasons.append(f"Sensitive keyword detected: '{kw}'")
            break

    # 4. Check Retrieval Confidence
    best_score = 0.0
    if context_chunks:
        best_score = max([c["score"] for c in context_chunks])
        if best_score < config.SIMILARITY_THRESHOLD:
            reasons.append(f"Low retrieval confidence: {best_score} (Threshold: {config.SIMILARITY_THRESHOLD})")
    else:
        reasons.append("No relevant documentation found in knowledge base.")

    # 5. Check Persistent Dissatisfaction
    # Count consecutive Angry/Frustrated turns in the conversation history
    frustrated_count = 0
    # Include latest turn
    if sentiment == "Angry/Frustrated":
        frustrated_count += 1
    # Check history
    for msg in reversed(chat_history):
        if msg.get("role") == "user":
            user_sentiment = msg.get("sentiment", "Neutral")
            if user_sentiment == "Angry/Frustrated":
                frustrated_count += 1
            else:
                break  # Only count consecutive
                
    if frustrated_count >= config.MAX_DISSATISFIED_TURNS:
        reasons.append(f"Persistent user dissatisfaction ({frustrated_count} consecutive turns).")

    # If any reason triggers, escalate
    if reasons:
        # Generate Handoff Summary
        handoff_summary = generate_handoff_summary(
            user_query=user_query,
            persona=persona,
            sentiment=sentiment,
            context_chunks=context_chunks,
            chat_history=chat_history,
            escalation_reasons=reasons,
            best_confidence=best_score
        )
        return {
            "escalated": True,
            "reason": "; ".join(reasons),
            "handoff_summary": handoff_summary
        }

    return {
        "escalated": False,
        "reason": None,
        "handoff_summary": None
    }

def generate_handoff_summary(
    user_query: str,
    persona: str,
    sentiment: str,
    context_chunks: list[dict],
    chat_history: list[dict],
    escalation_reasons: list[str],
    best_confidence: float
) -> dict:
    """Compiles a detailed, structured JSON handoff data for an escalating support ticket."""
    
    # Extract attempted steps by looking at previous assistant responses
    attempted_steps = []
    for msg in chat_history:
        if msg.get("role") == "assistant" and "response" in msg:
            # Get first line or summarize response
            resp_summary = msg["response"].split("\n")[0][:60]
            attempted_steps.append(resp_summary)

    # Format documents used
    documents_used = list(set([c["source"] for c in context_chunks])) if context_chunks else []

    # Map recommended action based on reason
    reasons_str = "; ".join(escalation_reasons)
    if "billing" in reasons_str.lower() or "refund" in reasons_str.lower() or "charge" in reasons_str.lower():
        recommendation = "Verify customer invoice history and initiate billing refund/adjustment verification in Stripe admin."
    elif "delete" in reasons_str.lower() or "cancel" in reasons_str.lower():
        recommendation = "Review account verification status, confirm deletion request with user, and coordinate database clean-up."
    elif "low retrieval" in reasons_str.lower() or "no relevant" in reasons_str.lower():
        recommendation = "Locate custom solution for undocumented query and update the knowledge base once resolved."
    elif "frustration" in reasons_str.lower() or "persistent" in reasons_str.lower():
        recommendation = "Immediate priority voice or direct chat outreach. Empathize and expedite technical diagnostic review."
    else:
        recommendation = "Analyze conversation history and troubleshoot the system integration error."

    # Structured handoff payload
    handoff = {
        "persona": persona,
        "sentiment": sentiment,
        "detected_issue": user_query[:120],
        "escalation_reasons": escalation_reasons,
        "documents_used": documents_used,
        "attempted_steps": attempted_steps,
        "best_retrieved_confidence": best_confidence,
        "recommended_next_steps": recommendation
    }
    
    return handoff
