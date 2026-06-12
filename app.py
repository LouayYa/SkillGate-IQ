import json
import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
HISTORY_FILE = "chat_history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def is_out_of_scope(curator: dict) -> bool:
    """True when the request isn't a learning / certification request."""
    if curator.get("in_scope") is False:
        return True
    lc = curator.get("learner_context") or {}
    has_learner = bool(lc.get("learner_id") or lc.get("certification_target"))
    has_content = any([
        curator.get("required_skills"),
        curator.get("skill_gaps"),
        curator.get("recommended_resources"),
    ])
    return not has_learner and not has_content


def session_title(curator: dict) -> str:
    lc = curator.get("learner_context") or {}
    wiq = (curator.get("work_iq_findings") or {}).get("learner") or {}
    name = wiq.get("name") or lc.get("learner_id") or "Learner"
    cert = lc.get("certification_target")
    return f"{name} · {cert}" if cert else name


@app.route("/")
def index():
    return render_template("index.html", history=load_history())


@app.route("/history/<session_id>")
def get_session(session_id):
    history = load_history()
    session = next((s for s in history if s["id"] == session_id), None)
    if not session:
        return {"error": "Not found"}, 404
    return session


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    is_followup = data.get("is_followup", False)
    previous_context = data.get("previous_context", None)

    def generate():
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from agents.learning_path_curator import run_learning_path_curator
            from agents.study_plan_reasoner import run_study_plan_reasoner
            from agents.learning_report_agent import run_learning_report_agent

            # Step 1 — Learning Path Curator
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'curator', 'message': 'Curating learning path — retrieving cited content and learner work context...'})}\n\n"

            if is_followup and previous_context:
                enriched = f"{user_message}\n\nContext from previous analysis:\n{json.dumps(previous_context)}"
            else:
                enriched = user_message

            curator = run_learning_path_curator(enriched)

            if is_out_of_scope(curator):
                reason = (curator.get("refusal_reason") or "").strip()
                hint = (
                    "SkillGate IQ only helps with certification study plans and learning "
                    "readiness — name a learner and a certification goal, e.g. “Help L-2002 "
                    "prepare for ACP-CE1 in 6 weeks.”"
                )
                yield f"data: {json.dumps({'type': 'refusal', 'message': (reason + ' ' + hint) if reason else hint})}\n\n"
                return

            rs = curator.get('required_skills') or []
            sg = curator.get('skill_gaps') or []
            cf = curator.get('capacity_flags') or []
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'curator', 'message': f'{len(rs)} required skills · {len(sg)} skill gaps · {len(cf)} capacity flags'})}\n\n"

            # Step 2 — Study Plan & Readiness Reasoner
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'reasoner', 'message': 'Building capacity-aware study plan — running critic loop...'})}\n\n"
            plan = run_study_plan_reasoner(curator)
            cl = plan.get('critic_loop_summary', {})
            self_check = 'passed' if cl.get('self_check_passed') else 'failed'
            mil = plan.get('study_plan', {}).get('milestones', [])
            reasoner_msg = f"Readiness {plan.get('readiness_score')}/100 · {len(mil)} milestones · self-check {self_check}"
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'reasoner', 'message': reasoner_msg})}\n\n"

            # Step 3 — Learning Report & Manager Insights
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'report', 'message': 'Generating learning readiness brief and manager insights...'})}\n\n"
            report = run_learning_report_agent(plan, curator.get("learner_context"))
            r = report.get('report', {})
            report_msg = f"{len(r.get('study_plan', {}).get('milestones', []))} milestones · {len(r.get('practice_questions', []))} practice questions"
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'report', 'message': report_msg})}\n\n"

            # Save to history
            history = load_history()
            title = session_title(curator)
            if is_followup:
                session = next((s for s in history if s["id"] == session_id), None)
                if session:
                    session["messages"].append({"role": "user", "content": user_message})
                    session["messages"].append({"role": "assistant", "report": report, "plan": plan, "curator": curator})
                    session["updated_at"] = datetime.now().isoformat()
            else:
                history.insert(0, {
                    "id": session_id,
                    "title": title,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "messages": [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "report": report, "plan": plan, "curator": curator},
                    ],
                })
            save_history(history)

            yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id, 'title': title, 'report': report, 'plan': plan, 'curator': curator})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
