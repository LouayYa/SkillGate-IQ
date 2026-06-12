import json
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from agents._shared import parse_agent_json, with_retry

load_dotenv()


def run_learning_report_agent(plan_output: dict, learner_context: dict = None) -> dict:
    client = AIProjectClient(
        endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()

    # The Report Agent receives the study-plan output, which has no learner
    # identity fields — so include learner_context so it can fill the header.
    payload = dict(plan_output)
    if learner_context:
        payload["learner_context"] = learner_context
    input_text = json.dumps(payload)

    response = with_retry(lambda: openai_client.responses.create(
        input=[{"role": "user", "content": input_text}],
        extra_body={
            "agent_reference": {
                "name": os.getenv("REPORT_AGENT_NAME", "learning-report-agent"),
                "version": os.getenv("REPORT_AGENT_VERSION", "1"),
                "type": "agent_reference",
            }
        },
    ))

    result = parse_agent_json(getattr(response, "output_text", ""), "Learning Report Agent")

    # Deterministic backfill so the report header is always populated.
    if learner_context and isinstance(result.get("report"), dict):
        rep = result["report"]
        for field in ("learner_id", "role", "certification_target"):
            if not rep.get(field):
                rep[field] = learner_context.get(field, "")

    return result
