"""Work IQ MCP client — Enterprise Learning System.

Spawns the Work IQ MCP server (workiq/server.py) over stdio, looks up the
learner named in the request, and assembles a structured ``work_iq_findings``
dict for the Learning Path Curator.

Fail-safe: any error returns None and the pipeline continues using the
knowledge base + the request text alone. Work IQ must never break a demo.
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TIMEOUT_SECONDS = 20


def _extract_tool_payload(result) -> dict:
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured.get("result", structured)
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                continue
    return {}


async def _fetch(request_text: str) -> dict:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "workiq.server"],
        cwd=_PROJECT_ROOT,
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            profile = _extract_tool_payload(
                await session.call_tool("get_learner_profile", {"learner": request_text})
            )
            learner = profile.get("learner")
            team_payload = {}
            if learner and learner.get("team"):
                team_payload = _extract_tool_payload(
                    await session.call_tool("get_team_signals", {"team": learner["team"]})
                )

    return {
        "learner": learner,
        "learner_found": bool(profile.get("found")),
        "team_signals": team_payload.get("team_signals"),
        "source_note": profile.get("source_note"),
    }


def get_work_iq_context(request_text: str) -> dict | None:
    """Return assembled Work IQ learner context, or None if unavailable. Never raises."""
    try:
        return asyncio.run(asyncio.wait_for(_fetch(request_text), _TIMEOUT_SECONDS))
    except Exception as e:  # noqa: BLE001 - Work IQ is optional
        print(f"[workiq] context unavailable, continuing without it: {e}", file=sys.stderr)
        return None


def format_for_prompt(findings: dict) -> str:
    """Render Work IQ findings as a prompt block for the Learning Path Curator."""
    if not findings or not findings.get("learner"):
        return ""
    return (
        "WORK IQ CONTEXT (synthetic Microsoft 365 work signals for this learner — "
        "meeting load, focus time, preferred learning slot, and study history). Use "
        "this to populate learner_context.work_signals, to size a realistic study "
        "plan against available focus hours, and to raise capacity_flags when the "
        "recommended study hours exceed what the learner's focus time allows:\n"
        + json.dumps(findings, indent=2)
    )


if __name__ == "__main__":
    demo = "Help L-2001 prepare for ACP-DO2 in the next 8 weeks."
    print(json.dumps(get_work_iq_context(demo), indent=2))
