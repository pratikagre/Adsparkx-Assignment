import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_genai_client():
    """Initializes the Gemini client using the environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    else:
        return genai.Client()

def classify_customer_persona(user_message: str, chat_history: str = "") -> dict:
    """
    Analyzes the user's message and historical context to classify it into one of three target personas:
    - Technical Expert
    - Frustrated User
    - Business Executive
    
    Also detects sentiment, urgency, and provides reasoning.
    """
    client = get_genai_client()

    system_instruction = (
        "You are an advanced classification engine for customer support. Your task is to analyze "
        "the tone, vocabulary, and sentiment of an incoming customer message (along with any provided chat history) "
        "and classify it into exactly one of three customer personas:\n"
        "1. 'Technical Expert': Uses technical jargon, asks about APIs, code, logs, configs, databases, or specific implementation details.\n"
        "2. 'Frustrated User': Uses emotional language, capitalization, exclamation marks, expresses anger, impatience, or mentions severe urgency.\n"
        "3. 'Business Executive': Focuses on business impact, ROI, service level agreements (SLA), timelines, cost, and brevity. Avoids technical details.\n\n"
        "Additionally, detect the sentiment ('Positive', 'Neutral', 'Angry/Frustrated') and urgency ('Low', 'Medium', 'High').\n"
        "Provide your evaluation strictly in the requested JSON structure."
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "persona": {
                "type": "STRING",
                "enum": ["Technical Expert", "Frustrated User", "Business Executive"]
            },
            "sentiment": {
                "type": "STRING",
                "enum": ["Positive", "Neutral", "Angry/Frustrated"]
            },
            "urgency": {
                "type": "STRING",
                "enum": ["Low", "Medium", "High"]
            },
            "reasoning": {"type": "STRING"}
        },
        "required": ["persona", "sentiment", "urgency", "reasoning"]
    }

    input_content = user_message
    if chat_history:
        input_content = f"Chat History:\n{chat_history}\n\nLatest Customer Message:\n{user_message}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=input_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "persona": "Frustrated User" if "urgent" in user_message.lower() or "!" in user_message else "Technical Expert" if "api" in user_message.lower() or "code" in user_message.lower() else "Business Executive",
            "sentiment": "Neutral",
            "urgency": "Medium",
            "reasoning": f"Fallback classification due to API error: {str(e)}"
        }

if __name__ == "__main__":
    test_msg = "Our production API key stopped working with a 401 Unauthorized block. Check our logs immediately."
    print("Testing classification with message:", test_msg)
    print(classify_customer_persona(test_msg))
