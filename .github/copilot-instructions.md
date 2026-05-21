# Copilot Instructions for the-lazy-gorgeous-warden

This document provides guidance for Copilot sessions working on this AI-powered file system auditor.

## Project Overview

**the-lazy-gorgeous-warden** is an automated file organization and auditing system that:
- Enforces a 5-tier directory hierarchy (01_Personal_Documents through 05_Device_Backups)
- Uses Google Gemini AI to classify misplaced files and suggest renames
- Validates naming conventions (DevOps standards: snake_case, kebab-case, SemVer)
- Operates in dry-run mode by default for safety
- Maintains detailed audit logs with emoji-enhanced console output

## Architecture

The project follows a **manifest-driven AI design** with four focused modules:

| Module | Responsibility |
|--------|-----------------|
| **warden.py** | Main orchestrator — entry point that coordinates the full audit pipeline (handshake → hierarchy → audit → classification). Calls all other modules in sequence. |
| **config.py** | Central configuration hub — loads `.env` credentials, defines the 5-tier folder hierarchy, manages ignore lists, and sets up structured logging with RotatingFileHandler. |
| **ai_engine.py** | Gemini API wrapper — handles model discovery with caching, automatic retry/backoff on quota errors (HTTP 429), and prompt construction for classification/renaming tasks. |
| **file_manager.py** | Filesystem layer — reads the `.warden-manifest.md` rules, enforces directory hierarchy, validates names via regex, performs recursive audit, and executes file operations. |

**Key Design Patterns:**
- **Layered separation**: Each module has a single responsibility and imports only what it needs
- **Manifest-driven**: Rules are loaded from `.warden-manifest.md` (target storage) rather than hard-coded
- **Dry-run first**: All operations are simulated by default; set `DRY_RUN=false` in `.env` to execute live
- **Quota-aware model fallback**: free-tier quota is per-model, so the engine can fall back to alternate models to reset counters

## Running and Testing

### Development Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with your TARGET_DIRECTORY and GOOGLE_API_KEY
```

### Running the Warden
```bash
# Dry-run (default safe mode)
python warden.py

# Live mode (only after testing)
# Edit .env: DRY_RUN=false, then:
python warden.py
```

### Code Quality
The project uses **ruff** for linting and **bandit** for security scanning (enforced in CI/CD via `quality.yml`):

```bash
# Lint check (same as CI)
ruff check .

# Security scan (same as CI)
bandit -r .

# Both (what runs in CI)
pip install ruff bandit
ruff check . --output-format github
bandit -r . -f txt
```

## Key Conventions

### Naming Standards
- **DevOps-compliant names**: Enforce `[a-zA-Z0-9_\-\.]+` (letters, numbers, underscores, hyphens, dots)
- **Validation occurs on**: File names and directory names (but ignores the extension)
- Function: `file_manager.is_valid_name(name)` returns True for compliant names

### Configuration via Environment
- **API Key**: `GOOGLE_API_KEY` — required from Google AI Studio (https://aistudio.google.com/app/apikey)
- **Target Directory**: `TARGET_DIRECTORY` — absolute path to audit (e.g., `/run/media/user/external_hd`)
- **Execution Mode**: `DRY_RUN=true` (default) or `false` for live mode
- **Logging Level**: `LOG_LEVEL=INFO|DEBUG|WARNING` (defaults to INFO)

### Module Imports and Logging
Each module initializes its own logger via `logger = logging.getLogger("warden")` — this ensures all output is unified under one logger.

### Error Handling
- **Quota errors (429)**: Caught in `ai_engine.py` with exponential backoff and model fallback
- **Missing files**: Gracefully handled (manifest returns default rules, missing folders are created)
- **Filesystem errors**: Logged but do not crash the application

### Audit Output
Logs are dual-stream:
1. **Console**: Emoji-enhanced, human-readable output
2. **File**: Rotating file handler (warden_audit.log, max 5 MB, 3 backups) with timestamps

## Important Implementation Details

### AI Model Selection
- Models are cached in memory (`_available_models`) to avoid repeated discovery calls
- Priority list: `gemini-2.5-flash` → `gemini-2.0-flash` → `gemini-1.5-flash`
- Filters out unsuitable models (TTS, image-gen, embedding, etc.) based on keyword exclusions

### File Classification Pipeline
1. **Audit**: Recursively scan target directory for orphans (files outside required folders) and naming violations
2. **Manifest Loading**: Read `.warden-manifest.md` for custom AI rules (or use sensible defaults)
3. **AI Analysis**: Send findings to Gemini for classification/renaming suggestions
4. **Execution**: Move files (if not dry-run) and log results

### Ignore List
Default ignore list in `config.py`:
```python
IGNORE_LIST = [
    "lost+found", ".trash", ".warden-manifest.md",
    ".env", ".git", ".DS_Store", ".Trash-1000", ".Trash-100"
]
```
These items are skipped during audits.

## When Modifying Code

- **Adding new AI capabilities**: Extend `ai_engine.py` with new functions, using existing retry/caching patterns
- **Changing filesystem operations**: Update `file_manager.py` and ensure both dry-run and live modes are tested
- **New configuration options**: Add to `config.py` (load from `.env`, document in `.env.example`)
- **Logging changes**: Preserve emoji output; use `logger.info()`, `logger.warning()`, `logger.error()`, `logger.critical()`
- **Testing changes**: Run `ruff check .` and `bandit -r .` before committing

## Common Workflows

### Adding a New Classification Rule
1. Edit `.warden-manifest.md` (on target storage) with new category rules
2. Modify `ai_engine.suggest_renames()` or `ai_engine.analyze_orphans()` prompts to reference the new rule
3. Test in dry-run mode first

### Extending Model Support
1. Add model name to `MODEL_PRIORITY` list in `ai_engine.py`
2. Add to `_EXCLUDED_KEYWORDS` if the model is unsuitable
3. Restart to clear model cache

### Debugging Audit Results
1. Set `LOG_LEVEL=DEBUG` in `.env` for verbose output
2. Check `warden_audit.log` for timestamp-stamped records
3. Use dry-run to see what would happen without risk
