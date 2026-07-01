from app.core.config import settings
from app.services.ai_client import call_llm, parse_json_response

print(f"Provider: {settings.AI_PROVIDER}")
print(f"Model: {settings.OPENAI_MODEL}")
print("Testing OpenAI connection...")

try:
    response = call_llm(
        "You are a helpful assistant. Reply with valid JSON only.",
        'Reply with: {"status": "ok", "message": "OpenAI connected"}'
    )
    data = parse_json_response(response.content)
    print(f"Response: {data}")
    print(f"Tokens used: {response.prompt_tokens} prompt + {response.completion_tokens} completion")
    print("\nOpenAI API key is working correctly!")
except Exception as e:
    print(f"Error: {e}")
