import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

import src.config as config

load_dotenv()

def get_genai_client():
    """Initializes the Gemini client using the environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    else:
        return genai.Client()

def generate_adaptive_response(user_query: str, persona: str, context_chunks: list[dict], chat_history: str = "") -> str:
    """
    Generates a personalized response matching the classified user persona,
    grounded only in the retrieved document chunks.
    """
    client = get_genai_client()

    # 1. Select persona-specific instructions
    if persona == "Technical Expert":
        persona_instructions = (
            "You are a Senior Technical Support Engineer at Adsparkx Cloud Services. "
            "Your writing style is highly detail-oriented, analytical, and structured. "
            "Provide root-cause explanations, specify exact API parameters, request body models, "
            "config settings, or step-by-step terminal commands where appropriate. "
            "Structure your answer with markdown headings and syntax-highlighted code blocks if relevant."
        )
    elif persona == "Frustrated User":
        persona_instructions = (
            "You are an empathetic, reassuring, and warm Customer Care Lead at Adsparkx Cloud Services. "
            "Your writing style is gentle, simple, and reassuring. "
            "Begin by validating their feelings and apologizing sincerely for the inconvenience. "
            "Use clear, jargon-free explanations. Structure your troubleshooting steps into simple, "
            "numbered actions or bullet points so they are easy to read and execute. "
            "Reassure them that you are there to help them resolve this immediately."
        )
    else:  # Business Executive
        persona_instructions = (
            "You are a concise, outcome-focused Customer Success Director at Adsparkx Cloud Services. "
            "Your writing style is brief, highly professional, direct, and focused on business outcomes. "
            "Highlight the operational impact, resolution timelines, and next steps immediately. "
            "Skip granular configuration instructions, code details, and technical logs. "
            "Provide estimated time to resolution (ETR) or support SLAs if mentioned in the text, "
            "or explain how we are addressing the business continuity aspect."
        )

    # 2. Format context text
    if context_chunks:
        context_text = "\n\n".join(
            [f"--- Document: {chunk['source']} (Confidence Similarity Score: {chunk['score']}) ---\n{chunk['text']}" 
             for chunk in context_chunks]
        )
    else:
        context_text = "NO CONTEXT DOCUMENTS AVAILABLE."

    # 3. Formulate the system instruction
    system_instruction = (
        f"{persona_instructions}\n\n"
        "CRITICAL BEHAVIOR RULES:\n"
        "- Answer the customer query using ONLY the information provided in the FACTUAL CONTEXT DOCUMENTS below.\n"
        "- Do not hallucinate, assume, or extrapolate facts that are not explicitly stated in the context.\n"
        "- If the query cannot be answered using the provided context documents, say exactly: "
        "'I apologize, but I do not have enough information in my knowledge base to answer your query. "
        "I will now connect you with a live support representative.'\n"
        "- Never mention 'according to the documents' or 'context indicates' - speak as the support agent directly.\n\n"
        f"FACTUAL CONTEXT DOCUMENTS:\n{context_text}"
    )

    # 4. Include chat history if available
    contents = []
    if chat_history:
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"Conversation History:\n{chat_history}\n\nLatest Query:\n{user_query}")]
        ))
    else:
        contents.append(user_query)

    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2  # Keep temperature low for facts/grounding
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"
