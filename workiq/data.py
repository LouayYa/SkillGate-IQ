"""Synthetic Work IQ data store — Enterprise Learning System.

All identifiers, people, teams and metrics below are FABRICATED for
demonstration. No real names, no PII. This stands in for the Microsoft 365
work signals a live Work IQ connection would surface for each learner:
meeting load, focus time, preferred learning slot, and study history.

Designed to line up with the knowledge base:
  - Certifications: ACP-CE1, ACP-DO2, ACP-DE1, ACP-SA4  (see LRN-CAT-001)
  - Roles & sequencing                                   (see LRN-MAP-002)
  - Capacity thresholds: >20 meeting hrs/wk = at risk;
    optimal 12-18 meeting + >=15 focus hrs/wk            (see LRN-WL-006)

The learners are deliberately varied so the Study Plan & Readiness Reasoner has
distinct cases to reason over — capacity-constrained, on-track, not-ready, and
exam-ready.
"""

# The person operating SkillGate IQ. In a live Work IQ deployment this would be
# the authenticated Microsoft 365 user (here, a synthetic L&D manager persona).
CURRENT_USER = {
    "employee_id": "MGR-3001",
    "name": "Robin Calloway",
    "role": "Learning & Development Manager",
    "department": "Engineering Enablement",
    "scope": "Owns certification readiness for Teams Alpha, Bravo and Charlie.",
}

# Per-learner work context, keyed by learner_id. work_signals field names match
# the Learning Path Curator's `work_signals` schema exactly.
LEARNERS = {
    "L-2001": {
        "learner_id": "L-2001",
        "name": "Maya Okonkwo",
        "role": "DevOps Engineer",
        "team": "Team Alpha",
        "target_certification": "ACP-DO2",
        "work_signals": {
            "meeting_hours_per_week": 16,
            "focus_hours_per_week": 16,
            "preferred_learning_slot": "Morning",
        },
        "study_history": {
            "practice_score_avg": 88,
            "hours_studied": 26,
            "prior_outcome": "ACP-CE1 passed",
            "last_activity": "approx. 2 days ago",
        },
        "context_note": (
            "Four weeks on: meeting load eased to 16 hrs/wk with 16 focus hrs/wk, "
            "practice average up to 88% (above the 75% target), and 26 hours logged "
            "(exceeds the 25-hour ACP-DO2 recommendation) — now on track / exam-ready."
        ),
    },
    "L-2002": {
        "learner_id": "L-2002",
        "name": "Diego Alvarez",
        "role": "Cloud Engineer",
        "team": "Team Bravo",
        "target_certification": "ACP-CE1",
        "work_signals": {
            "meeting_hours_per_week": 16,
            "focus_hours_per_week": 17,
            "preferred_learning_slot": "Afternoon",
        },
        "study_history": {
            "practice_score_avg": 78,
            "hours_studied": 18,
            "prior_outcome": "none",
            "last_activity": "approx. 2 days ago",
        },
        "context_note": (
            "Healthy capacity (16 meeting / 17 focus hrs). Above the 75% practice "
            "target and close to the 20-hour recommendation for ACP-CE1 — on track."
        ),
    },
    "L-2003": {
        "learner_id": "L-2003",
        "name": "Priya Nair",
        "role": "Data Engineer",
        "team": "Team Charlie",
        "target_certification": "ACP-DE1",
        "work_signals": {
            "meeting_hours_per_week": 13,
            "focus_hours_per_week": 20,
            "preferred_learning_slot": "Morning",
        },
        "study_history": {
            "practice_score_avg": 71,
            "hours_studied": 14,
            "prior_outcome": "none",
            "last_activity": "approx. 3 days ago",
        },
        "context_note": (
            "Strong focus time (20 hrs/wk). Slightly below the 75% practice target "
            "and the 22-hour recommendation for ACP-DE1 — on track with a little more "
            "practice on weaker skills."
        ),
    },
    "L-2004": {
        "learner_id": "L-2004",
        "name": "Sam Turner",
        "role": "Cloud Engineer",
        "team": "Team Bravo",
        "target_certification": "ACP-SA4",
        "work_signals": {
            "meeting_hours_per_week": 18,
            "focus_hours_per_week": 15,
            "preferred_learning_slot": "Evening",
        },
        "study_history": {
            "practice_score_avg": 55,
            "hours_studied": 6,
            "prior_outcome": "ACP-CE1 passed",
            "last_activity": "approx. 5 days ago",
        },
        "context_note": (
            "Targeting the Expert-level ACP-SA4 (30 rec. hours, 80% target) but only "
            "6 hours studied and 55% practice average — not ready; needs a longer, "
            "front-loaded plan."
        ),
    },
    "L-2005": {
        "learner_id": "L-2005",
        "name": "Lena Fischer",
        "role": "DevOps Engineer",
        "team": "Team Charlie",
        "target_certification": "ACP-DO2",
        "work_signals": {
            "meeting_hours_per_week": 12,
            "focus_hours_per_week": 22,
            "preferred_learning_slot": "Morning",
        },
        "study_history": {
            "practice_score_avg": 82,
            "hours_studied": 26,
            "prior_outcome": "ACP-CE1 passed",
            "last_activity": "approx. 1 day ago",
        },
        "context_note": (
            "Exceeds both the 25-hour recommendation and the 75% practice target for "
            "ACP-DO2, with ample focus time — exam-ready / on track."
        ),
    },
}

# Team-level aggregates for manager insights. Mirrors the capacity snapshot in
# LRN-WL-006 so the Report Agent's manager_insights line up with the KB rules.
TEAMS = {
    "Team Alpha": {
        "team": "Team Alpha",
        "members": ["L-2001"],
        "avg_meeting_hours_per_week": 24,
        "avg_focus_hours_per_week": 9,
        "completion_trend": "Below target — capacity constrained",
    },
    "Team Bravo": {
        "team": "Team Bravo",
        "members": ["L-2002", "L-2004"],
        "avg_meeting_hours_per_week": 16,
        "avg_focus_hours_per_week": 17,
        "completion_trend": "On target",
    },
    "Team Charlie": {
        "team": "Team Charlie",
        "members": ["L-2003", "L-2005"],
        "avg_meeting_hours_per_week": 13,
        "avg_focus_hours_per_week": 20,
        "completion_trend": "Above target",
    },
}

SOURCE_NOTE = (
    "Synthetic Microsoft 365 work signals (Work IQ pattern). This is demonstration "
    "data, not a live tenant connection. Learners are referenced by fabricated IDs."
)
