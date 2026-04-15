import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai  # Modern 2026 SDK

# --- 1. Configuration & Environment ---
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

TARGET_DIR = os.getenv("TARGET_DIRECTORY", "your_path_directory")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
API_KEY = os.getenv("GOOGLE_API_KEY")

# Official English Hierarchy for the Warden
REQUIRED_FOLDERS = [
    "01_Personal_Documents",
    "02_Digital_Gallery",
    "03_Studies_and_Career",
    "04_Entertainment",
    "05_Device_Backups"
]

# System items to ignore during audit
IGNORE_LIST = ["lost+found", ".trash", ".picasaoriginals", "$RECYCLE.BIN"]

def initialize_warden():
    """Initializes the modern Google AI Client"""
    if not API_KEY:
        print(f"❌ Error: GOOGLE_API_KEY not found in {ENV_PATH}")
        return None
    try:
        # New 2026 SDK Syntax
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def check_naming_violation(name):
    """Checks for spaces or special characters"""
    invalid_chars = " !@#$%^&*()+=[]{}|\\;:'\",<>?/"
    return any(char in name for char in invalid_chars)

def audit_patrol(target_path):
    """Main audit logic using the new target path"""
    print(f"\n🎩 THE-LAZY-GORGEOUS-WARDEN is now patrolling: {target_path}")
    print("-" * 60)
    
    path = Path(target_path)
    
    if not path.exists():
        print(f"❌ Error: Target directory '{target_path}' not found.")
        return

    orphans = []
    naming_violations = []

    try:
        for item in path.iterdir():
            # Skip items in the ignore list
            if item.name in IGNORE_LIST:
                continue
                
            # Check for Orphan Files/Folders
            if item.name not in REQUIRED_FOLDERS:
                orphans.append(item)
            
            # Check for Naming Violations
            if check_naming_violation(item.name):
                naming_violations.append(item.name)
    except PermissionError:
        print("❌ Error: Permission denied to access the target directory.")
        return

    # --- REPORTING ---
    if orphans:
        print(f"⚠️  ORPHAN ALERT: Found {len(orphans)} items outside the hierarchy:")
        for orphan in orphans:
            type_str = "[DIR] " if orphan.is_dir() else "[FILE]"
            print(f"   {type_str} {orphan.name}")
    else:
        print("✅ No orphans found (ignoring system folders). Root items are clean.")

    if naming_violations:
        print(f"\n📝 NAMING ALERT: Found {len(naming_violations)} items with naming issues:")
        for violation in naming_violations:
            print(f"   [!] {violation}")
    else:
        print("\n✅ All filenames are terminal-friendly.")

    print("-" * 60)
    print(f"Status: {'SIMULATION (Dry Run)' if DRY_RUN else 'LIVE MODE'}")

if __name__ == "__main__":
    client = initialize_warden()
    
    if client:
        print(f"✨ AI Connection Established via {ENV_PATH.name}")
        audit_patrol(TARGET_DIR)
    else:
        print("🛑 Warden could not start due to configuration issues.")
