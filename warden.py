import ai_engine
import file_manager
import config

# ---------------------------------------------------------------------------
# Initialise structured logging before anything else
# ---------------------------------------------------------------------------
logger = config.setup_logging()


def main():
    logger.info("🚀 Starting The-Lazy-Gorgeous-Warden...")

    # 1. Initialize Client with strict validation
    client = ai_engine.get_client()
    if not client:
        logger.critical("🛑 Warden could not start. Check your .env configuration.")
        return

    # 2. Load manifest rules
    rules = file_manager.load_manifest()

    # 3. Handshake and Basic Infrastructure Provisioning
    if ai_engine.verify_awareness(client, rules):
        # Phase 4: Auto-create official folders if missing
        file_manager.ensure_hierarchy()

        # 4. Deep Audit (Recursive Orphans and Naming Violations)
        orphans, naming_violations = file_manager.audit_directory()

        # 5. Handle Naming Violations (Recursive Results)
        if naming_violations:
            logger.warning(
                "🚫 NAMING VIOLATIONS: %d item(s) detected.", len(naming_violations)
            )
            for violation in naming_violations:
                logger.warning("   - %s", violation)

            # Phase 5.4: AI Renaming Intelligence
            rename_pairs = ai_engine.suggest_renames(client, naming_violations)

            # Phase 5.5: Execute Renames
            if rename_pairs:
                ok, fail = file_manager.execute_renames(rename_pairs)
                logger.info(
                    "📊 Rename results: %d succeeded, %d failed/skipped.", ok, fail
                )

        # 6. Handle Root Orphans
        if orphans:
            logger.warning(
                "⚠️  ORPHANS DETECTED: %d item(s) found at root.", len(orphans)
            )
            # Phase 5.1: AI Classification Intelligence
            ai_engine.analyze_orphans(client, rules, orphans)

        # 7. Final Report
        if not orphans and not naming_violations:
            logger.info("✅ Structure and Naming are compliant. No action needed.")
    else:
        logger.critical(
            "🛑 Warden failed the consciousness check. "
            "Verify your API key or connection."
        )

    # Metadata and Status Label
    status_label = "SIMULATION" if config.DRY_RUN else "LIVE MODE"
    logger.info("\nFinal Status: %s", status_label)
    logger.info("🏁 Patrol finished.")


if __name__ == "__main__":
    main()
