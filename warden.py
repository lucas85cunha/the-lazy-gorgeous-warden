import ai_engine
import file_manager
import config

def main():
    print("🚀 Starting The-Lazy-Gorgeous-Warden...")
    
    # 1. Initialize AI Client with validation
    client = ai_engine.get_client()
    if not client:
        print("🛑 Warden could not start. Check your .env configuration.")
        return

    # 2. Load manifest rules with validation
    rules = file_manager.load_manifest()
    
    # 3. Handshake and Consciousness Check
    if ai_engine.verify_awareness(client, rules):
        # Phase 4: Infrastructure Provisioning
        # Ensures 01-05 folders exist before auditing
        file_manager.ensure_hierarchy()
        
        # 4. Deep Audit (Orphans and Naming)
        # Now receiving two distinct lists from the updated file_manager
        orphans, naming_violations = file_manager.audit_directory()
        
        # 5. Handle Naming Violations (Recursive results)
        if naming_violations:
            print(f"🚫 NAMING VIOLATIONS: {len(naming_violations)} item(s) are not snake_case.")
            for violation in naming_violations:
                print(f"   - {violation}")
            print("💡 Tip: Use lowercase, numbers, and underscores only.")

        # 6. Handle Orphans with AI Classification
        if orphans:
            print(f"⚠️  ORPHANS DETECTED: {len(orphans)} item(s) found at root.")
            ai_engine.analyze_orphans(client, rules, orphans)
        
        # 7. Final Compliance Check
        if not orphans and not naming_violations:
            print("✅ Structure and Naming are compliant. No action needed.")
    else:
        print("🛑 Warden failed the consciousness check. Verify your API key or connection.")
    
    # Final metadata
    status_label = "SIMULATION" if config.DRY_RUN else "LIVE MODE"
    print(f"\nFinal Status: {status_label}")
    print("🏁 Patrol finished.")

if __name__ == "__main__":
    main()
