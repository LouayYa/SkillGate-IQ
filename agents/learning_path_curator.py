import json
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from workiq.client import get_work_iq_context, format_for_prompt
from agents._shared import parse_agent_json, with_retry

load_dotenv()


def run_learning_path_curator(learner_request: str) -> dict:
    client = AIProjectClient(
        endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()

    # Work IQ context layer (synthetic learner work signals via local MCP server).
    # Fail-safe: None if unavailable, in which case we proceed on the KB alone.
    work_iq_findings = get_work_iq_context(learner_request)
    agent_input = learner_request
    if work_iq_findings:
        agent_input = learner_request + "\n\n" + format_for_prompt(work_iq_findings)

    response = with_retry(lambda: openai_client.responses.create(
        input=[{"role": "user", "content": agent_input}],
        extra_body={
            "agent_reference": {
                "name": os.getenv("CURATOR_AGENT_NAME", "learning-path-curator"),
                "version": os.getenv("CURATOR_AGENT_VERSION", "1"),
                "type": "agent_reference",
            }
        },
    ))

    result = parse_agent_json(getattr(response, "output_text", ""), "Learning Path Curator")
    result["work_iq_findings"] = work_iq_findings
    return result


if __name__ == "__main__":
    req = "Help L-2001, a DevOps Engineer, prepare for ACP-DO2 in the next 8 weeks."
    print(json.dumps(run_learning_path_curator(req), indent=2))
