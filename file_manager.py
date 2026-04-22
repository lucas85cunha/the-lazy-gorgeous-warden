import re
import logging
from pathlib import Path

import config

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
logger = logging.getLogger("warden")


def load_manifest():
    """Loads the AI rules from the Markdown manifesto."""
    manifest_path = Path(config.TARGET_DIR) / ".warden-manifest.md"
    if not manifest_path.exists():
        logger.warning("⚠️  Manifest not found at %s! Using default context.", manifest_path)
        return "Standard file organization rules apply: 5-tier hierarchy, DevOps naming."
    return manifest_path.read_text(encoding="utf-8")


def ensure_hierarchy():
    """Verifies and creates official folders if DRY_RUN is False."""
    logger.info("📂 Checking hierarchy in: %s", config.TARGET_DIR)
    target_path = Path(config.TARGET_DIR)

    if not target_path.exists():
        logger.error("❌ Error: Target path %s not found.", config.TARGET_DIR)
        return

    for folder in config.REQUIRED_FOLDERS:
        folder_path = target_path / folder
        if not folder_path.exists():
            if config.DRY_RUN:
                logger.debug("🔍 [DRY RUN] Would create folder: %s", folder)
            else:
                try:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    logger.info("✅ Folder created: %s", folder)
                except Exception as exc:
                    logger.error("❌ Failed to create %s: %s", folder, exc)


def is_valid_name(name):
    """Checks if a name follows DevOps standards (snake_case, kebab-case, or SemVer).

    Allows: letters (upper/lower), numbers, underscores, hyphens, and dots.
    Ignores the file extension for validation.
    """
    # Remove extension for validation (e.g., gets 'kali-linux-2025' from 'kali-linux-2025.iso')
    base_name = Path(name).stem

    # Regex updated: allows a-z, A-Z, 0-9, underscores (_), hyphens (-), and dots (.)
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    return bool(re.match(pattern, base_name))


def audit_directory():
    """Identifies items outside the required structure and naming violations."""
    logger.info("\n🎩 Patrolling: %s", config.TARGET_DIR)
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
        logger.error("❌ Error: Permission denied to access the directory.")
    except Exception as exc:
        logger.error("❌ Unexpected error during audit: %s", exc)

    return orphans, naming_violations


def execute_renames(rename_pairs):
    """Rename files on disk based on AI-suggested pairs.

    Each pair is ``(original_relative_path, suggested_file_name)``.
    The rename keeps the file in its original directory — only the
    file name changes.

    Respects ``config.DRY_RUN``: when True, only logs what *would* happen.

    Returns:
        tuple[int, int]: ``(success_count, failure_count)``
    """
    if not rename_pairs:
        return 0, 0

    target_path = Path(config.TARGET_DIR)
    success = 0
    failed = 0

    for original_rel, suggested_name in rename_pairs:
        source = target_path / original_rel
        destination = source.parent / suggested_name

        if not source.exists():
            logger.warning("⏭️  Skipping (not found): %s", source)
            failed += 1
            continue

        if destination.exists():
            logger.warning("⏭️  Skipping (target already exists): %s", destination)
            failed += 1
            continue

        if config.DRY_RUN:
            logger.debug("🔍 [DRY RUN] Would rename: %s -> %s", source.name, suggested_name)
            success += 1
        else:
            try:
                source.rename(destination)
                logger.info("✅ Renamed: %s -> %s", source.name, suggested_name)
                success += 1
            except Exception as exc:
                logger.error("❌ Failed to rename %s: %s", source.name, exc)
                failed += 1

    return success, failed
