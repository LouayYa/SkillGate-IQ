"""Shared helpers for the SkillGate IQ agents: robust JSON parsing and
rate-limit-aware retry around Foundry calls."""

import json
import random
import time


def parse_agent_json(raw_text: str, agent_label: str = "Agent") -> dict:
    """Parse the first JSON object out of an agent's text output.

    Handles two common quirks: JSON wrapped in ```json fences, and the same
    object emitted twice back-to-back (which makes plain json.loads fail with
    "Extra data"). JSONDecoder.raw_decode reads one value and ignores the rest.
    """
    text = (raw_text or "").strip()

    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
        return obj
    except json.JSONDecodeError as e:
        raise ValueError(
            f"{agent_label} returned invalid JSON.\nError: {e}\nRaw output:\n{text}"
        )


def with_retry(fn, retries: int = 4, base: float = 1.5, max_sleep: float = 20.0):
    """Call ``fn`` with exponential backoff on transient Foundry errors
    (HTTP 429 rate limits, timeouts, 503). Re-raises on non-transient errors
    and after the final attempt."""
    last_error = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - classify by message
            last_error = e
            msg = str(e).lower()
            transient = (
                "429" in msg or "rate limit" in msg or "rate_limit" in msg
                or "timeout" in msg or "timed out" in msg or "503" in msg
                or "temporarily unavailable" in msg
            )
            if not transient or attempt == retries - 1:
                raise
            time.sleep(min(base * (2 ** attempt) + random.uniform(0, 0.5), max_sleep))
    raise last_error
