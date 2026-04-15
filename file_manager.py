from pathlib import Path
import config

def load_manifest():
    manifest_path = Path(config.TARGET_DIR) / ".warden-manifest.md"
    if not manifest_path.exists():
        print(f"⚠️  Manifest not found at {manifest_path}! Using default context.")
        return "Standard file organization rules apply: 5-tier hierarchy, snake_case naming."
    return manifest_path.read_text(encoding="utf-8")

def ensure_hierarchy():
    """Verifies and creates official folders if DRY_RUN is False"""
    print(f"📂 Checking hierarchy in: {config.TARGET_DIR}")
    target_path = Path(config.TARGET_DIR)
    
    if not target_path.exists():
        print(f"❌ Error: Target path {config.TARGET_DIR} not found.")
        return

    for folder in config.REQUIRED_FOLDERS:
        folder_path = target_path / folder
        if not folder_path.exists():
            if config.DRY_RUN:
                print(f"🔍 [DRY RUN] Would create folder: {folder}")
            else:
                try:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Folder created: {folder}")
                except Exception as e:
                    print(f"❌ Failed to create {folder}: {e}")

def audit_directory():
    """Identifies items outside the required structure"""
    print(f"\n🎩 Patrolling: {config.TARGET_DIR}")
    path = Path(config.TARGET_DIR)
    
    orphans = []
    if not path.exists(): 
        return orphans

    try:
        for item in path.iterdir():
            if item.name in config.IGNORE_LIST:
                continue
            if item.name not in config.REQUIRED_FOLDERS:
                orphans.append(item.name)
    except PermissionError:
        print("❌ Error: Permission denied to access the directory.")
        
    return orphans
