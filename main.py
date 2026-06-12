import json

from agents.learning_path_curator import run_learning_path_curator
from agents.study_plan_reasoner import run_study_plan_reasoner
from agents.learning_report_agent import run_learning_report_agent


def main():
    print("=" * 60)
    print("  SkillGate IQ — Enterprise Learning Readiness")
    print("=" * 60)

    learner_request = (
        "Help L-2001, a DevOps Engineer, prepare for ACP-DO2 in the next 8 weeks."
    )

    print(f"\nRequest:\n{learner_request}\n")
    print("-" * 60)

    print("\n[1/3] Running Learning Path Curator...")
    curator = run_learning_path_curator(learner_request)
    if curator.get("in_scope") is False:
        print(f"  Out of scope: {curator.get('refusal_reason', 'Not a learning request.')}")
        return
    lc = curator.get("learner_context", {})
    print(f"  Learner:         {lc.get('learner_id')} ({lc.get('role')})")
    print(f"  Certification:   {lc.get('certification_target')}")
    print(f"  Required skills: {len(curator.get('required_skills', []))}")
    print(f"  Skill gaps:      {len(curator.get('skill_gaps', []))}")
    print(f"  Capacity flags:  {len(curator.get('capacity_flags', []))}")

    print("\n[2/3] Running Study Plan & Readiness Reasoner...")
    plan = run_study_plan_reasoner(curator)
    print(f"  Readiness:       {plan.get('readiness_status')} ({plan.get('readiness_score')}/100)")
    print(f"  Plan weeks:      {plan.get('study_plan', {}).get('total_weeks')}")
    print(f"  Milestones:      {len(plan.get('study_plan', {}).get('milestones', []))}")
    print(f"  Practice Qs:     {len(plan.get('practice_questions', []))}")
    cl = plan.get("critic_loop_summary", {})
    print(f"  Self-check:      {'Passed' if cl.get('self_check_passed') else 'Failed'}")

    print("\n[3/3] Running Learning Report Agent...")
    report = run_learning_report_agent(plan, curator.get("learner_context"))
    r = report["report"]
    print(f"  Learner:         {r.get('learner_id')}")
    print(f"  Readiness:       {r.get('readiness_status')} ({r.get('readiness_score')}/100)")
    print(f"  Milestones:      {len(r.get('study_plan', {}).get('milestones', []))}")

    print("\nSaving outputs...")
    with open("curator_output.json", "w") as f:
        json.dump(curator, f, indent=2)
    with open("plan_output.json", "w") as f:
        json.dump(plan, f, indent=2)
    with open("report_output.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("  Pipeline complete. Full report saved to report_output.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
