from google import genai
import config

def get_client():
    if not config.API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found.")
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
        target_model = next((m for m in available_models if "gemini-2.5-flash" in m), 
                       next((m for m in available_models if "gemini-1.5-flash" in m), 
                       available_models[0] if available_models else None))

        print(f"📡 Using model: {target_model}")
        config.SELECTED_MODEL = target_model # Store for later use
        
        prompt = f"SYSTEM RULES:\n{manifest_content}\n\nTask: Summarize mission in one short sentence."
        response = client.models.generate_content(model=target_model, contents=prompt)
        
        if response.text:
            print(f"🤖 Warden: {response.text.strip()}")
            return True
        return False
    except Exception as e:
        print(f"❌ Handshake Failed: {e}")
        return False

def analyze_orphans(client, manifest_content, orphans):
    """Asks the AI to suggest destinations for orphan items"""
    if not orphans:
        return
    
    print(f"🤔 Analyzing {len(orphans)} orphan(s) with AI...")
    
    # Prompting the AI to be a classifier
    prompt = f"""
    SYSTEM CONTEXT:
    {manifest_content}
    
    OFFICIAL DESTINATIONS:
    {config.REQUIRED_FOLDERS}
    
    TASK:
    Analyze the following orphan items and suggest the best official folder for each.
    If an item looks like system trash, suggest 'IGNORE'.
    Format: [Item Name] -> [Target Folder] (Reason)
    
    ORPHANS TO ANALYZE:
    {orphans}
    """
    
    try:
        response = client.models.generate_content(
            model=config.SELECTED_MODEL, 
            contents=prompt
        )
        print("\n💡 WARDEN'S CLASSIFICATION SUGGESTIONS:")
        print("-" * 40)
        print(response.text.strip())
        print("-" * 40)
    except Exception as e:
        print(f"⚠️  Could not classify orphans: {e}")
