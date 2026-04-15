import ai_engine
import file_manager
import config

def main():
    print("🚀 Starting The-Lazy-Gorgeous-Warden...")
    
    # 1. Initialize Client
    client = ai_engine.get_client()
    if not client:
        return

    # 2. Load manifest rules
    rules = file_manager.load_manifest()
    
    # 3. Handshake and Audit
    if ai_engine.verify_awareness(client, rules):
        # Phase 4: Auto-create official folders
        file_manager.ensure_hierarchy()
        
        # Orphan detection
        orphans = file_manager.audit_directory()
        
        if orphans:
            print(f"⚠️  ORPHANS DETECTED: {len(orphans)} item(s) outside the hierarchy.")
            for orphan in orphans:
                print(f"   - {orphan}")
        else:
            print("✅ Structure is compliant. All items are within the official hierarchy.")
    
    status_label = "SIMULATION" if config.DRY_RUN else "LIVE MODE"
    print(f"Final Status: {status_label}")
    print("\n🏁 Patrol finished.")

if __name__ == "__main__":
    main()
