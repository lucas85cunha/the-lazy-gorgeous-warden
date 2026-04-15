import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# --- 1. Configuration & Environment ---
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

TARGET_DIR = os.getenv("TARGET_DIRECTORY", "your_path_directory")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
API_KEY = os.getenv("GOOGLE_API_KEY")

REQUIRED_FOLDERS = [
    "01_Personal_Documents", 
    "02_Digital_Gallery", 
    "03_Studies_and_Career", 
    "04_Entertainment", 
    "05_Device_Backups"
]
IGNORE_LIST = ["lost+found", ".trash", ".warden-manifest.md", ".env", ".git", ".DS_Store"]

def initialize_warden():
    """Initializes the modern Google AI Client"""
    if not API_KEY:
        print(f"❌ Error: GOOGLE_API_KEY not found in {ENV_PATH}")
        return None
    try:
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def load_manifest(target_path):
    """Loads the AI rules from the Markdown manifesto"""
    manifest_path = Path(target_path) / ".warden-manifest.md"
    if not manifest_path.exists():
        print(f"⚠️  Manifest not found at {manifest_path}! Using default context.")
        return "Standard file organization rules: 5-tier hierarchy, snake_case naming."
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return "Standard rules."

def verify_ai_awareness(client, manifest_content):
    """Handshake: Ensures the AI understood the manifesto using dynamic model discovery"""
    print("🧠 Searching for available Gemini models...")
    
    try:
        # Dynamic Discovery: Asks the API which models are allowed for this key
        # This prevents 404 errors caused by region-specific naming
        available_models = [m.name for m in client.models.list()]
        
        # Priority 1: Gemini 1.5 Flash | Priority 2: Gemini 1.0 Pro | Fallback: First available
        target_model = next((m for m in available_models if "gemini-1.5-flash" in m), 
                       next((m for m in available_models if "gemini-1.0-pro" in m), 
                       available_models[0] if available_models else None))

        if not target_model:
            print("❌ No models found for this API Key.")
            return False

        print(f"📡 Using model: {target_model}")
        
        prompt = f"SYSTEM RULES:\n{manifest_content}\n\nTask: Summarize your mission in exactly one short sentence."
        
        response = client.models.generate_content(
            model=target_model, 
            contents=prompt
        )
        
        if response.text:
            print(f"🤖 Warden's Response: {response.text.strip()}")
            return True
        else:
            print("⚠️ AI responded but the text body was empty.")
            return False
            
    except Exception as e:
        print(f"❌ AI Handshake Failed: {e}")
        return False

def audit_patrol(target_path):
    """Main audit logic"""
    print(f"\n🎩 THE-LAZY-GORGEOUS-WARDEN is patrolling: {target_path}")
    print("-" * 60)
    
    path = Path(target_path)
    if not path.exists():
        print(f"❌ Error: Target directory '{target_path}' not found.")
        return

    orphans = []
    found_items = 0

    try:
        for item in path.iterdir():
            found_items += 1
            if item.name in IGNORE_LIST:
                continue
            if item.name not in REQUIRED_FOLDERS:
                orphans.append(item.name)
    except PermissionError:
        print("❌ Error: Permission denied to access the directory.")
        return

    if found_items == 0:
        print("Empty lot. The target directory is completely empty.")
    elif orphans:
        print(f"⚠️  ORPHANS DETECTED: Found {len(orphans)} item(s) outside the hierarchy:")
        for orphan in orphans:
            print(f"   - {orphan}")
    else:
        print("✅ Structure is compliant. All items are within the official hierarchy.")

    print("-" * 60)
    print(f"Status: {'SIMULATION (Dry Run)' if DRY_RUN else 'LIVE MODE'}")

if __name__ == "__main__":
    print("🚀 Starting the Warden...")
    
    client = initialize_warden()
    if client:
        print(f"✨ AI Connection Established via .env")
        
        rules = load_manifest(TARGET_DIR)
        print(f"📖 Rules loaded from directory: {TARGET_DIR}")
        
        if verify_ai_awareness(client, rules):
            audit_patrol(TARGET_DIR)
        else:
            print("🛑 Warden failed the consciousness check. Check connection or API permissions.")
    else:
        print("🛑 Warden could not start. Check your .env configuration.")
    
    print("\n🏁 Patrol finished.")
