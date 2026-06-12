"""Work IQ MCP server (synthetic) — Enterprise Learning System.

Exposes the per-learner Work IQ context layer as Model Context Protocol tools
over stdio. The SkillGate IQ orchestrator runs this as an MCP client (see
workiq/client.py) and injects the retrieved learner context into the Learning
Path Curator agent.

Run directly for a quick check:  python -m workiq.server
"""

import re

from fastmcp import FastMCP

from workiq.data import CURRENT_USER, LEARNERS, TEAMS, SOURCE_NOTE

mcp = FastMCP("workiq-learning")


def _match_learner(query: str):
    """Match a free-text query to a learner by ID (L-####) or name."""
    if not query:
        return None
    m = re.search(r"[Ll]-\d{3,}", query)
    if m:
        lid = m.group(0).upper()
        if lid in LEARNERS:
            return LEARNERS[lid]
    q = query.lower()
    for rec in LEARNERS.values():
        if rec["name"].lower() in q:
            return rec
    return None


@mcp.tool()
def get_learner_profile(learner: str) -> dict:
    """Return a learner's Work IQ profile: role, target certification, work
    signals (meeting hours, focus hours, preferred learning slot) and study
    history. Use this to judge how much the learner can realistically study and
    how close they are to readiness.

    Args:
        learner: A learner ID (e.g. "L-2001") or name mentioned in the request.
    """
    rec = _match_learner(learner)
    if rec is None:
        return {
            "found": False,
            "query": learner,
            "message": "No Work IQ profile found for this learner.",
            "source_note": SOURCE_NOTE,
        }
    return {"found": True, "learner": rec, "source_note": SOURCE_NOTE}


@mcp.tool()
def get_team_signals(team: str) -> dict:
    """Return a team's aggregate capacity signals (avg meeting hours, avg focus
    hours, completion trend) for manager-level insights.

    Args:
        team: A team name (e.g. "Team Alpha").
    """
    if team:
        for name, rec in TEAMS.items():
            if name.lower() in team.lower() or team.lower() in name.lower():
                return {"found": True, "team_signals": rec, "source_note": SOURCE_NOTE}
    return {"found": False, "team": team, "source_note": SOURCE_NOTE}


@mcp.tool()
def search_learners(query: str) -> dict:
    """Search learners by role, certification target, or team when the learner
    ID/name is unclear.

    Args:
        query: Free-text describing the learner(s) you are looking for.
    """
    q = (query or "").lower()
    hits = []
    for rec in LEARNERS.values():
        haystack = " ".join([
            rec["role"], rec["target_certification"], rec["team"]
        ]).lower()
        if any(tok in haystack for tok in q.split() if len(tok) > 2):
            hits.append(rec)
    return {"matches": hits, "operator": CURRENT_USER, "source_note": SOURCE_NOTE}


if __name__ == "__main__":
    mcp.run(show_banner=False)
