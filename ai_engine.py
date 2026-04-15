from google import genai
import config

def get_client():
    if not config.API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        return None
    try:
        return genai.Client(api_key=config.API_KEY)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def verify_awareness(client, manifest_content):
    print("🧠 Discovering available AI models...")
    try:
        available_models = [m.name for m in client.models.list()]
        
        # Priority: Gemini 2.5 Flash -> 1.5 Flash -> First available
        target_model = next((m for m in available_models if "gemini-2.5-flash" in m), 
                       next((m for m in available_models if "gemini-1.5-flash" in m), 
                       available_models[0] if available_models else None))

        print(f"📡 Using model: {target_model}")
        
        prompt = f"SYSTEM RULES:\n{manifest_content}\n\nTask: Summarize mission in one short sentence."
        response = client.models.generate_content(model=target_model, contents=prompt)
        
        if response.text:
            print(f"🤖 Warden: {response.text.strip()}")
            return True
        return False
    except Exception as e:
        print(f"❌ Handshake Failed: {e}")
        return False
