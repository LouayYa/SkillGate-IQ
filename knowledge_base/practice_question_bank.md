# Acme Corp Certification Practice Question Bank

**Document ID:** LRN-QB-004
**Owner:** Acme Corp Learning & Enablement Office
**Status:** Synthetic practice questions for demonstration only. Original content; not derived from any real certification exam.

These approved practice questions are the grounded source for generated assessment questions. Each is tagged with its certification, skill, and difficulty, and includes a model answer. Cite questions as `LRN-QB-004 §<certification> / <skill>`.

## ACP-CE1 — Acme Certified Cloud Engineer

**Q1 — Identity & Access Basics — foundational**
A service account needs to read from one storage bucket only. What is the correct approach?
*Model answer:* Grant a scoped, least-privilege role limited to that bucket rather than a broad account-wide role. Enable MFA on the account.

**Q2 — Storage & Data Services — foundational**
A workload stores large, rarely accessed log archives. Which storage choice minimises cost?
*Model answer:* Use object storage with a cold/archive tier and a lifecycle rule that transitions data after a set age.

**Q3 — Networking Essentials — intermediate**
How do you allow a web tier to reach a database tier while blocking direct internet access to the database?
*Model answer:* Place the database in a private subnet with no public route; allow inbound traffic only from the web tier's security group on the database port.

## ACP-DO2 — Acme Certified DevOps Professional

**Q1 — CI/CD Pipelines — intermediate**
What is the purpose of an automated quality gate between pipeline stages?
*Model answer:* It blocks promotion of a build that fails tests, scans, or policy checks, preventing defective artifacts from reaching later environments.

**Q2 — Secure DevOps — advanced**
How do you prevent secrets from being committed into source control within a pipeline?
*Model answer:* Add automated secret scanning as a pre-merge gate and store secrets in a managed secret store referenced at runtime, never in code.

**Q3 — Release Management — advanced**
Describe a canary release and one signal that should trigger an automatic rollback.
*Model answer:* Route a small percentage of traffic to the new version first; roll back automatically if error rate or latency exceeds the defined SLO threshold.

## ACP-DE1 — Acme Certified Data Engineer

**Q1 — Data Ingestion & Pipelines — foundational**
What distinguishes incremental ingestion from full reload, and when is incremental preferred?
*Model answer:* Incremental ingestion loads only new or changed records using a watermark; it is preferred for large, frequently updated sources to reduce cost and runtime.

**Q2 — Batch & Stream Processing — advanced**
What is a tumbling window in stream processing?
*Model answer:* A fixed-size, non-overlapping time window; each event belongs to exactly one window, used for periodic aggregations.

**Q3 — Data Security & Governance — intermediate**
How do you protect personally sensitive columns while still allowing analytics?
*Model answer:* Apply column-level masking or tokenisation and classify the data so access policies and lineage tracking are enforced.

## ACP-SA4 — Acme Certified Solutions Architect

**Q1 — High Availability & Disaster Recovery — advanced**
A service requires a 15-minute recovery point. What does this imply for backup design?
*Model answer:* Backups or replication must capture changes at least every 15 minutes (RPO ≤ 15 min), typically via continuous or near-continuous replication.

**Q2 — Migration Strategy — advanced**
In the 6 Rs framework, when would you choose "replatform" over "rehost"?
*Model answer:* Choose replatform when small optimisations (e.g. moving to a managed database) yield meaningful benefit without a full rewrite; rehost ("lift and shift") makes no changes.

**Q3 — Security Architecture — advanced**
State one core principle of a zero-trust boundary.
*Model answer:* Never trust by network location; authenticate and authorise every request explicitly, regardless of whether it originates inside or outside the network.
