import re
from pathlib import Path
import config

def load_manifest():
    """Loads the AI rules from the Markdown manifesto"""
    manifest_path = Path(config.TARGET_DIR) / ".warden-manifest.md"
    if not manifest_path.exists():
        print(f"⚠️  Manifest not found at {manifest_path}! Using default context.")
        return "Standard file organization rules apply: 5-tier hierarchy, DevOps naming."
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

def is_valid_name(name):
    """
    Checks if a name follows DevOps standards (snake_case, kebab-case, or SemVer).
    Allows: letters (upper/lower), numbers, underscores, hyphens, and dots.
    Ignores the file extension for validation.
    """
    # Remove extension for validation (e.g., gets 'kali-linux-2025' from 'kali-linux-2025.iso')
    base_name = Path(name).stem
    
    # Regex updated: allows a-z, A-Z, 0-9, underscores (_), hyphens (-), and dots (.)
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    return bool(re.match(pattern, base_name))

def audit_directory():
    """Identifies items outside the required structure and naming violations"""
    print(f"\n🎩 Patrolling: {config.TARGET_DIR}")
    path = Path(config.TARGET_DIR)
    
    orphans = []
    naming_violations = []
    
    if not path.exists():
        return orphans, naming_violations

    try:
        # 1. Level 1 Audit: Orphans at the root
        for item in path.iterdir():
            if item.name in config.IGNORE_LIST:
                continue
            
            if item.name not in config.REQUIRED_FOLDERS:
                orphans.append(item.name)
            
            # 2. Level 2 Audit: Recursive naming check inside official folders
            if item.is_dir() and item.name in config.REQUIRED_FOLDERS:
                # rglob('*') finds everything recursively
                for sub_item in item.rglob('*'):
                    if sub_item.name in config.IGNORE_LIST:
                        continue
                    
                    # Updated to use the new valid naming rule
                    if not is_valid_name(sub_item.name):
                        # Store relative path for better reporting
                        relative_path = sub_item.relative_to(path)
                        naming_violations.append(str(relative_path))

    except PermissionError:
        print("❌ Error: Permission denied to access the directory.")
    except Exception as e:
        print(f"❌ Unexpected error during audit: {e}")
        
    return orphans, naming_violations
