import json
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from agents._shared import parse_agent_json, with_retry

load_dotenv()


def run_study_plan_reasoner(curator_output: dict) -> dict:
    client = AIProjectClient(
        endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()

    input_text = json.dumps(curator_output)

    response = with_retry(lambda: openai_client.responses.create(
        input=[{"role": "user", "content": input_text}],
        extra_body={
            "agent_reference": {
                "name": os.getenv("REASONER_AGENT_NAME", "study-plan-reasoner"),
                "version": os.getenv("REASONER_AGENT_VERSION", "1"),
                "type": "agent_reference",
            }
        },
    ))

    return parse_agent_json(getattr(response, "output_text", ""), "Study Plan & Readiness Reasoner")
