import time
import logging

from google import genai
from google.genai import errors as genai_errors

import config

# ---------------------------------------------------------------------------
# Module-level logger & constants
# ---------------------------------------------------------------------------
logger = logging.getLogger("warden")

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 5

# Preferred model order — free-tier quota is **per model**, so falling back
# to a different model effectively resets the 20 req/day counter.
MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# In-memory caches (avoids repeated discovery calls within a session)
_available_models: list[str] | None = None   # full list from API
_active_model: str | None = None             # currently selected model


# ---------------------------------------------------------------------------
# Model discovery with cache & fallback
# ---------------------------------------------------------------------------
def _discover_models(client):
    """Fetch and cache the list of text-capable Gemini models from the API.

    Filters out specialty models (TTS, image-gen, robotics, embedding, etc.)
    that support ``generateContent`` but cannot produce standard text output.
    """
    global _available_models
    if _available_models is not None:
        return _available_models

    logger.info("🧠 Discovering available AI models...")

    # Suffixes / keywords that indicate a model is NOT suitable for text gen
    _EXCLUDED_KEYWORDS = (
        "-tts", "-image", "-robotics", "-computer-use",
        "embedding", "gemma", "lyria", "nano-", "deep-research",
        "imagen", "veo", "aqa", "native-audio", "-live",
    )

    _available_models = [
        m.name
        for m in client.models.list()
        if not any(kw in m.name for kw in _EXCLUDED_KEYWORDS)
    ]
    return _available_models


def _select_best_model(client, *, exclude: set[str] | None = None):
    """Pick the highest-priority model that is not in the *exclude* set.

    Priority order (configurable via ``MODEL_PRIORITY``):
        1. ``gemini-2.5-flash``
        2. ``gemini-2.0-flash``
        3. ``gemini-1.5-flash``
        4. First remaining model returned by the API
    """
    global _active_model
    available = _discover_models(client)
    exclude = exclude or set()

    for preferred in MODEL_PRIORITY:
        match = next(
            (m for m in available if preferred in m and m not in exclude),
            None,
        )
        if match:
            _active_model = match
            config.SELECTED_MODEL = _active_model
            logger.info("📡 Using model: %s", _active_model)
            return _active_model

    # Last resort: pick any model not yet excluded
    fallback = next((m for m in available if m not in exclude), None)
    if fallback:
        _active_model = fallback
        config.SELECTED_MODEL = _active_model
        logger.warning("📡 Falling back to model: %s", _active_model)
        return _active_model

    logger.error("❌ No available models left (all exhausted or excluded).")
    return None


# ---------------------------------------------------------------------------
# Resilient API wrapper with automatic model fallback
# ---------------------------------------------------------------------------
def _call_with_retry(client, callable_fn, *args, **kwargs):
    """Retry wrapper for Gemini API calls.

    Strategy on HTTP 429 (quota exceeded):
        1. Try exponential backoff on the **same model** up to ``MAX_RETRIES``.
        2. If retries are exhausted, **switch to the next available model**
           (free-tier quota is per-model) and retry once with the new model.
    """
    exhausted_models: set[str] = set()

    while True:
        current_model = _active_model
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return callable_fn(*args, **kwargs)
            except genai_errors.ClientError as exc:
                if exc.code != 429:
                    raise

                if attempt < MAX_RETRIES:
                    delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                    logger.warning(
                        "⏳ Quota exceeded (429). Retry %d/%d in %ds...",
                        attempt, MAX_RETRIES, delay,
                    )
                    time.sleep(delay)
                else:
                    # All retries failed for this model — try the next one
                    exhausted_models.add(current_model)
                    logger.warning(
                        "🔄 Model %s quota exhausted. Searching for fallback...",
                        current_model,
                    )
                    new_model = _select_best_model(
                        client, exclude=exhausted_models,
                    )
                    if not new_model:
                        raise  # no models left — propagate original error

                    # Patch the model kwarg for the next attempt
                    if "model" in kwargs:
                        kwargs["model"] = new_model
                    break  # restart the retry loop with the new model
        else:
            # Inner loop completed without break → success already returned
            break


# ---------------------------------------------------------------------------
# Client initialisation
# ---------------------------------------------------------------------------
def get_client():
    """Initializes the Gemini API Client."""
    if not config.API_KEY:
        logger.error("❌ Error: GOOGLE_API_KEY not found in environment.")
        return None
    try:
        return genai.Client(api_key=config.API_KEY)
    except Exception as exc:
        logger.error("❌ Connection Error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# AI-powered analysis functions
# ---------------------------------------------------------------------------
def verify_awareness(client, manifest_content):
    """Handshake: Ensures the AI understands the organization manifest."""
    target_model = _select_best_model(client)
    if not target_model:
        return False

    prompt = (
        f"SYSTEM RULES:\n{manifest_content}\n\n"
        "Task: Summarize mission in one short sentence."
    )

    try:
        response = _call_with_retry(
            client,
            client.models.generate_content,
            model=target_model,
            contents=prompt,
        )
        if response.text:
            logger.info("🤖 Warden: %s", response.text.strip())
            return True
        return False
    except Exception as exc:
        logger.error("❌ Handshake Failed: %s", exc)
        return False


def analyze_orphans(client, manifest_content, orphans):
    """Asks the AI to suggest destinations for orphan items at the root."""
    if not orphans:
        return

    logger.info("🤔 Analyzing %d orphan(s) with AI...", len(orphans))

    prompt = f"""\
SYSTEM CONTEXT:
{manifest_content}

OFFICIAL DESTINATIONS:
{config.REQUIRED_FOLDERS}

TASK:
Analyze the following orphan items and suggest the best official folder for each.
Format: [Item Name] -> [Target Folder] (Reason)

ORPHANS TO ANALYZE:
{orphans}
"""

    try:
        response = _call_with_retry(
            client,
            client.models.generate_content,
            model=config.SELECTED_MODEL,
            contents=prompt,
        )
        logger.info("\n💡 WARDEN'S CLASSIFICATION SUGGESTIONS:")
        logger.info("-" * 40)
        logger.info(response.text.strip())
        logger.info("-" * 40)
    except Exception as exc:
        logger.warning("⚠️  Could not classify orphans: %s", exc)


def suggest_renames(client, violations):
    """Ask the AI for clean file names and return structured rename pairs.

    Returns:
        list[tuple[str, str]]: A list of ``(original_relative_path,
        suggested_file_name)`` pairs.  Returns an empty list on failure.
    """
    if not violations:
        return []

    logger.info("🤔 Asking AI to fix %d naming violation(s)...", len(violations))

    prompt = f"""\
TASK:
The following file paths violate our DevOps naming standard (spaces, special chars, etc).
Please suggest a corrected, clean **file name** (not the full path) for each.

RULES:
1. Use ONLY lowercase letters, numbers, underscores (_), hyphens (-), and dots (.).
2. Convert spaces to hyphens.
3. Remove accents and special characters.
4. Keep the original file extension.

IMPORTANT: Respond ONLY with a valid JSON array. No markdown, no explanation.
Each element must be an object with "original" (the full relative path as given)
and "suggested" (only the corrected file name, not the path).

Example:
[{{"original": "folder/Bad File Name.pdf", "suggested": "bad-file-name.pdf"}}]

VIOLATIONS TO FIX:
{violations}
"""

    try:
        response = _call_with_retry(
            client,
            client.models.generate_content,
            model=config.SELECTED_MODEL,
            contents=prompt,
        )

        raw = response.text.strip()
        # Strip markdown code fences if the model wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]  # remove first line (```json)
            raw = raw.rsplit("```", 1)[0]  # remove closing ```
            raw = raw.strip()

        import json
        pairs = json.loads(raw)

        rename_map = []
        for entry in pairs:
            original = entry.get("original", "")
            suggested = entry.get("suggested", "")
            if original and suggested:
                rename_map.append((original, suggested))

        logger.info("\n💡 WARDEN'S RENAMING SUGGESTIONS:")
        logger.info("-" * 60)
        for orig, new in rename_map:
            logger.info("  %s -> %s", orig, new)
        logger.info("-" * 60)

        return rename_map

    except Exception as exc:
        logger.warning("⚠️  Could not generate renaming suggestions: %s", exc)
        return []

