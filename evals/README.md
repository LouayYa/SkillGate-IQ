# SkillGate IQ — Evaluation Dataset

`eval_dataset.jsonl` is a small synthetic benchmark used to measure the **quality
and safety** of SkillGate IQ's readiness assessments in the **Microsoft Foundry
portal**. It holds five learner scenarios — covering all three outcomes (On
track, At risk, Not ready) plus one out-of-scope request — and is scored with
Foundry's built-in evaluators (Groundedness, Relevance, Similarity, and the
safety suite) to verify that the system's verdicts are **grounded in the
knowledge base, relevant to the request, and free of harmful content**.

Each row has four fields:
- `query` — the learner request
- `context` — the approved knowledge-base facts the answer should be grounded in
- `response` — the system's readiness verdict + rationale (**the text being judged**)
- `ground_truth` — the expected correct verdict (reference for Similarity)

> For a fully truthful eval, replace each `response` with the **actual output**
> from running that scenario in the app. The pre-filled responses are
> representative of the live behaviour (the L-2001 row matches the real run).

## Run it in the Foundry portal

1. Open your project in **Azure AI Foundry** (ai.azure.com).
2. Left nav → **Evaluation** → **+ New evaluation**.
3. Data source → **Upload dataset** → select `eval_dataset.jsonl`.
4. **Map columns:** `query` → query, `response` → response, `context` → context,
   `ground_truth` → ground truth.
5. **Select evaluators:** Groundedness, Relevance, Coherence (+ Similarity, which
   uses `ground_truth`).
6. **Grader model:** choose your `gpt-4o-mini` deployment as the judge model.
7. **Run**, then review the per-row and aggregate scores. Screenshot the results
   for the README / demo.

The guardrail row ("What's the weather...") is best read as a refusal check
rather than a groundedness score.
