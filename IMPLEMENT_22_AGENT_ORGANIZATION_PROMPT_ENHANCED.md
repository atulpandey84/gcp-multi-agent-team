# AI AGENT IMPLEMENTATION PROMPT
# Complete and Operationalize the 22-Agent GCP Landing Zone Engineering Organization

## Document Role

You are an AI coding/implementation agent working on the **GCP Multi-Agent
Engineering Team** repository.

This prompt is an implementation directive that extends the existing
`IMPLEMENT_22_AGENT_ORGANIZATION_PROMPT.md` with the latest requirements from
the authoritative `MULTI_AGENT_TEAM_SPECIFICATION.md`.

The authoritative specification defines the organizational model, governance,
agent personas, permissions, memory, workflows, evaluation, repository
structure, operational infrastructure, and production controls.

**SOURCE-OF-TRUTH RULE**

```text
MULTI_AGENT_TEAM_SPECIFICATION.md
                |
                +--> Agent Personas
                +--> System Prompts
                +--> Tool Permissions
                +--> Memory Schemas
                +--> Workflow Graphs
                +--> Agent Registry
                +--> Security Policies
                +--> Evaluation Tests
                +--> Repository Structure
                |
                v
          LangGraph / ADK
```

Framework implementation must never become the source of truth.

---

# 1. MISSION

Transform the current approximately 25%-complete multi-agent framework into a
**fully operational, governed 22-agent engineering organization** capable of
designing, implementing, securing, testing, deploying, operating, and learning
from enterprise GCP Landing Zone workloads.

The organization must behave like a real engineering organization rather than
a collection of chatbot personas.

It must:

- decompose engineering objectives
- create dependency-aware work
- route work to specialist agents
- enforce authority boundaries
- collect objective evidence
- perform real peer review
- enforce separation of duties
- enforce quality/security/FinOps gates
- require human approval for high-risk actions
- maintain persistent organizational memory
- maintain a complete audit trail
- observe its own performance and cost
- learn from deployments, incidents, tests, security findings and costs
- fail closed when evidence is insufficient

---

# 2. CURRENT FOUNDATION — PRESERVE IT

The existing implementation contains useful foundational concepts that MUST be
preserved and operationalized rather than replaced unnecessarily:

- `AgentContract`
- `AgentMemory`
- Task lifecycle
- `AgentMessage`
- collaboration framework
- `PeerReviewRequest`
- `CollaborationEvidence`
- `SeparationOfDutiesCheck`
- contract validation

The previous review identified these gaps:

1. Hollow registry
2. Stub agents
3. Declarative rather than operational collaboration
4. Separation-of-duties not enforced in workflow paths
5. Evidence not wired to real tools
6. Dependency management not operational
7. Quality gates not blocking execution
8. Memory not fully integrated
9. Auditability incomplete
10. End-to-end workflow incomplete

Do not merely add classes or documentation. **Make the code operational.**

---

# 3. NON-NEGOTIABLE ENGINEERING PRINCIPLES

## 3.1 Agents are bounded specialists

Every agent MUST have:

- bounded mission
- explicit authority
- explicit limitations
- specialized tools
- persistent memory where appropriate
- structured inputs
- structured outputs
- escalation rules
- measurable Definition of Done
- model policy
- security/data classification

Agents are not generic chatbots.

## 3.2 Separation of duties

No single agent may independently:

```text
DESIGN
  +
IMPLEMENT
  +
APPROVE
  +
DEPLOY
  +
VALIDATE
```

a high-risk change.

## 3.3 Human-in-the-loop

Human approval is mandatory for:

- production destructive changes
- security exceptions
- compliance exceptions
- IAM privilege escalation
- organization-level policy changes
- production database destruction
- production networking changes with material blast radius
- major architecture exceptions
- material unbudgeted cloud expenditure
- external organizational communication

## 3.4 Evidence over assertions

Evidence priority:

1. repository evidence
2. architecture artifacts
3. automated tests
4. runtime telemetry
5. GCP configuration
6. approved documentation
7. trusted external documentation
8. reasoned assumptions

Assumptions MUST be explicitly labeled.

## 3.5 Everything important becomes an artifact

Important decisions must produce durable artifacts:

- ADRs
- requirements
- architecture diagrams
- threat models
- test plans
- Terraform changes
- runbooks
- incident reports
- cost reports
- release records

## 3.6 Fail closed

When sufficient evidence is unavailable for a high-impact decision:

```text
DO NOT GUESS
DO NOT FABRICATE
DO NOT AUTO-APPROVE
REQUEST EVIDENCE OR ESCALATE
```

---

# 4. THE 22-AGENT ORGANIZATION

The authoritative agent IDs are:

| # | Agent ID | Role | Team |
|---|---|---|---|
| 01 | `product_owner` | Product Owner | Product |
| 02 | `project_manager` | Project Manager | Delivery |
| 03 | `engineering_orchestrator` | Engineering Orchestrator | Engineering Governance |
| 04 | `platform_architect` | Platform Architect | Architecture |
| 05 | `solution_architect` | Solution Architect | Architecture |
| 06 | `security_architect` | Security Architect | Architecture |
| 07 | `devops_lead` | DevOps Lead | DevOps |
| 08 | `cloud_infrastructure_engineer` | Cloud Infrastructure Engineer | DevOps |
| 09 | `cicd_engineer` | CI/CD Engineer | DevOps |
| 10 | `sre_observability_engineer` | SRE / Observability Engineer | DevOps |
| 11 | `finops_engineer` | FinOps Engineer | DevOps |
| 12 | `development_lead` | Development Lead | Development |
| 13 | `frontend_engineer` | Frontend Engineer | Development |
| 14 | `backend_engineer` | Backend Engineer | Development |
| 15 | `integration_engineer` | Integration Engineer | Development |
| 16 | `ai_automation_engineer` | AI / Automation Engineer | Development |
| 17 | `qa_lead` | QA Lead | Testing |
| 18 | `test_automation_engineer` | Test Automation Engineer | Testing |
| 19 | `nfr_test_engineer` | NFR Test Engineer | Testing |
| 20 | `application_management_lead` | Application Management Lead | Application Management |
| 21 | `application_support_engineer` | Application Support Engineer | Application Management |
| 22 | `production_reliability_engineer` | Production Reliability Engineer | Application Management |

If the repository's specification contains an updated authoritative list,
follow the specification and update this table accordingly.

---

# 5. AGENT CONTRACT REQUIREMENTS

Every agent MUST be instantiated with a complete contract containing at least:

```yaml
agent_id:
name:
role:
team:
mission:
system_prompt:
authority:
limitations:
capabilities:
allowed_tools:
forbidden_tools:
inputs:
outputs:
memory_scope:
model_policy:
risk_level:
dependencies:
reviewers:
escalation_rules:
collaboration_rules:
definition_of_done:
data_classification:
```

Registry initialization MUST fail if any mandatory field is absent.

No production registry entry may be `None`.

---

# 6. REAL AGENT EXECUTION

Every agent must execute a real lifecycle:

```text
RECEIVE TASK
     |
VALIDATE CONTRACT
     |
CHECK AUTHORITY
     |
CHECK DEPENDENCIES
     |
CHECK REQUIRED EVIDENCE
     |
EXECUTE
     |
COLLECT TOOL EVIDENCE
     |
UPDATE MEMORY
     |
PRODUCE ARTIFACTS
     |
REQUEST REVIEW
     |
QUALITY GATE
     |
APPROVAL IF REQUIRED
     |
COMPLETE
```

Agents MUST NOT return placeholder values such as:

```python
{"collaborated": True}
```

unless that value is a genuine result of an actual collaboration operation.

---

# 7. TASK LIFECYCLE

The canonical lifecycle is:

```text
CREATED
  ↓
TRIAGED
  ↓
PLANNED
  ↓
ASSIGNED
  ↓
IN_PROGRESS
  ↓
WAITING_FOR_DEPENDENCY
  ↓
REVIEW
  ↓
QUALITY_GATE
  ↓
APPROVAL
  ↓
READY_FOR_RELEASE
  ↓
RELEASED
  ↓
VALIDATED
  ↓
DONE
```

Failure states:

```text
BLOCKED
ESCALATED
FAILED
ROLLED_BACK
CANCELLED
```

No illegal state transition may be permitted.

---

# 8. TASK DECOMPOSITION AND DEPENDENCY GRAPH

`EngineeringOrchestratorAgent` MUST decompose engineering objectives into a
real task graph.

Example:

```text
Requirements
     |
     +--> Platform Architecture
     |
     +--> Solution Architecture
     |
     +--> Security Architecture
     |
     +--> FinOps
     |
     +--> Operations
              |
              v
         Implementation
              |
              v
         Testing/Validation
              |
              v
          Peer Review
              |
              v
         Quality Gates
              |
              v
       Human Approval
              |
              v
           Release
```

Every task must contain:

- task ID
- parent task
- assigned agent
- dependencies
- inputs
- expected outputs
- required evidence
- risk level
- review requirements
- Definition of Done
- state
- retry policy
- escalation policy

Dependency failures MUST propagate to dependent tasks.

---

# 9. OPERATIONAL COLLABORATION

Collaboration must execute, not merely log.

Implement and use:

```python
request_peer_review()
submit_review()
record_collaboration_evidence()
get_review_status()
verify_review_requirements()
```

A review rejection MUST block downstream execution.

Peer review must be independent where required.

The author cannot be the sole approver of high-risk work.

---

# 10. EVIDENCE REGISTRY

Implement a persistent `EvidenceRegistry`.

Evidence schema:

```yaml
evidence_id:
task_id:
agent_id:
type:
source:
timestamp:
content_reference:
hash:
validation_status:
confidence:
```

Evidence sources include:

- repository files
- Git history
- Terraform
- `terraform fmt`
- `terraform validate`
- `terraform plan`
- unit tests
- integration tests
- security scans
- static analysis
- GCP APIs
- logs
- metrics
- traces
- configuration
- peer reviews
- approvals

Generated reasoning is NOT sufficient evidence for high-risk decisions.

---

# 11. TOOL EXECUTION

Implement a `ToolRegistry` and `ToolAuthorization` layer.

Execution flow:

```text
Agent
  |
  v
Tool Registry
  |
  v
Permission Check
  |
  v
Risk Classification
  |
  v
Environment Policy
  |
  v
SoD Check
  |
  v
Approval Check
  |
  v
Execute
  |
  v
ToolResult
  |
  v
EvidenceRegistry
```

Every meaningful tool call produces a structured `ToolResult`.

---

# 12. GCP / TERRAFORM TOOLING

The system must provide controlled adapters for:

```text
GCP
Terraform
Git
CI/CD
Testing
Security
FinOps
Observability
```

At minimum, support adapter interfaces for:

```text
gcp_read
terraform_fmt
terraform_validate
terraform_plan
terraform_apply
terraform_destroy
git_read
git_diff
git_status
run_tests
run_lint
security_scan
cost_analysis
metrics_read
logs_read
```

High-risk tools such as:

```text
terraform_apply
terraform_destroy
production IAM modification
organization policy modification
production networking modification
```

must be approval-aware and policy-controlled.

---

# 13. EVIDENCE FROM TOOLS

A successful tool call is not automatically equivalent to business correctness.

For example:

```python
terraform_validate()
```

must generate evidence such as:

```yaml
tool: terraform_validate
status: SUCCESS
exit_code: 0
stdout_reference:
stderr_reference:
evidence_id:
timestamp:
```

The evidence must be registered and referenced by the resulting task.

---

# 14. SEPARATION OF DUTIES

Integrate:

```python
check_separation_of_duties()
```

into actual workflow execution.

Examples:

```text
Developer
    |
    v
Implementation
    |
    v
Independent Review
    |
    v
Security / QA Validation
    |
    v
Approval
    |
    v
Deployment
```

Violations MUST block execution.

---

# 15. QUALITY GATES

Implement executable gates:

```text
REQUIREMENTS_GATE
ARCHITECTURE_GATE
SECURITY_GATE
FINOPS_GATE
CODE_QUALITY_GATE
TEST_GATE
NFR_GATE
OPERATIONAL_READINESS_GATE
PRODUCTION_APPROVAL_GATE
```

Each gate must define:

- required evidence
- reviewers
- pass criteria
- failure criteria
- audit record

No gate may pass because an agent merely states that it passed.

---

# 16. AI GOVERNANCE

Implement production-grade AI governance.

Required controls:

- model registry
- prompt versioning
- tool registry
- agent registry
- evaluation datasets
- prompt-injection testing
- tool authorization
- output validation
- sensitive-data detection
- audit logging
- cost monitoring
- human approval for high-risk actions

No agent should have unrestricted access to:

- production credentials
- secrets
- personal data
- financial data
- organization-level IAM
- unrestricted external systems

unless explicitly authorized.

---

# 17. MODEL REGISTRY AND NVIDIA NIM

Use the model configuration already present in the repository.

The specification currently defines NVIDIA AI Endpoints as the primary provider
using:

```text
NVIDIA_API_KEY
```

The active model policies include:

```text
deepseek-ai/deepseek-v4-pro
deepseek-ai/deepseek-v4-flash
nvidia/nemotron-3-ultra-550b-a55b
nvidia/nemotron-3-super-120b-a12b
```

Do NOT hard-code these names into agent implementations.

Use:

```text
config/models.yaml
```

and a model router.

The model router must support policies such as:

```text
architecture_critical
senior_reasoning
coding
fast_agent
fast_coding
security_critical
review
orchestration
```

Every model invocation must record:

- provider
- model
- policy
- endpoint/host
- latency
- token usage where available
- fallback status
- failure reason if applicable

Before modifying model assignments, inspect the current NVIDIA model catalog
and the repository configuration. Do not assume a model is available merely
because it appears in an old document.

---

# 18. SMART OLLAMA FALLBACK

The repository specification requires intelligent fallback from NVIDIA AI
Endpoints to Ollama.

Support:

```text
OLLAMA_LOCAL_URL
OLLAMA_REMOTE_URL
```

Current configured examples are:

```text
OLLAMA_LOCAL_URL=http://192.168.31.135:11434
OLLAMA_REMOTE_URL=http://192.168.31.63:11434
```

Do NOT blindly hard-code these values into application code.

Read them from environment/configuration.

Fallback decision should consider:

- NVIDIA availability
- HTTP errors
- timeout
- latency
- local Ollama health
- remote Ollama health
- responsiveness
- hardware/load metrics where available

The fallback router must record:

```yaml
primary_provider:
primary_model:
fallback_provider:
fallback_model:
reason:
health_status:
selected_host:
```

Fallback must not bypass security, tool permissions, or approval policies.

---

# 19. POSTGRESQL PERSISTENCE

The authoritative specification now requires PostgreSQL as the mandatory
production persistence layer.

Use PostgreSQL database:

```text
agent_memory
```

SQLite must NOT be introduced as a production alternative.

PostgreSQL must support persistence for:

- agent state
- task state
- workflow state
- audit trails
- approvals
- institutional memory
- episodic memory
- evidence metadata
- collaboration records
- review records
- vector/semantic memory where implemented
- model execution records
- cost records

Use a repository/service abstraction so storage implementation remains
testable.

For local development, PostgreSQL should still be the default architecture.

Do not silently replace PostgreSQL with SQLite.

---

# 20. MEMORY ARCHITECTURE

Implement distinct memory scopes:

```text
Agent Memory
Project Memory
Organizational Memory
Episodic Memory
Semantic/Vector Memory
```

Memory must retain:

- decisions
- ADR references
- task outcomes
- review outcomes
- evidence references
- incidents
- security findings
- cost observations
- deployment outcomes
- lessons learned

Memory is contextual.

Evidence remains authoritative for proof.

---

# 21. OBSERVABILITY OF THE AGENT PLATFORM

Track at least:

- agent invocation count
- task success rate
- task failure rate
- tool errors
- token/model consumption
- cost per task
- human escalation rate
- approval latency
- retry rate
- workflow duration
- quality gate failure rate
- security violation attempts
- hallucination/error indicators
- agent-to-agent communication volume
- model fallback rate
- evidence validation failures

Expose structured telemetry.

Prepare interfaces for:

- OpenTelemetry
- LangSmith
- Prometheus-compatible metrics
- structured JSON logs

External observability services must remain optional for local development.

---

# 22. AUDITABILITY

Create durable audit events for:

- task creation
- task assignment
- agent execution
- tool invocation
- evidence creation
- evidence validation
- review request
- review result
- gate result
- approval request
- approval result
- deployment
- rollback
- escalation
- failure
- model selection
- model fallback
- security policy violation

Start with a PostgreSQL-backed implementation consistent with the mandatory
database architecture.

---

# 23. AGENT FAILURE POLICY

Agents must distinguish:

- temporary tool failure
- insufficient information
- invalid requirement
- dependency failure
- implementation failure
- security failure
- quality failure
- authorization failure

Failure must never be hidden.

Use a structured failure object:

```yaml
failure:
  task_id:
  agent:
  failure_type:
  description:
  attempted_actions:
  evidence:
  impact:
  recommended_next_action:
  escalation_target:
```

---

# 24. ARTIFACT GENERATION

Agents must create real project artifacts.

Examples:

### Product Owner
- product requirements
- acceptance criteria
- priorities

### Project Manager
- plan
- milestones
- dependency map
- delivery status

### Platform Architect
- GCP landing zone architecture
- platform standards
- organization/folder/project model

### Solution Architect
- solution architecture
- integration architecture
- service interactions

### Security Architect
- threat model
- IAM model
- security controls
- security exceptions

### DevOps
- Terraform
- CI/CD
- deployment pipelines
- observability

### Development
- application code
- APIs
- integrations
- automation

### Testing
- test strategy
- automated tests
- NFR results

### Application Management
- runbooks
- support model
- SLO/SLI definitions
- operational readiness
- incident procedures

### FinOps
- cost model
- budgets
- labels/tags
- optimization recommendations

---

# 25. ADR GOVERNANCE

No agent may silently replace an approved architecture.

Architecture changes must create an ADR containing:

```text
Context
Decision
Alternatives
Consequences
Security Impact
Operational Impact
FinOps Impact
Status
Approvals
```

Architecture exceptions require appropriate review and, when required, human
approval.

---

# 26. AGENT EVALUATION FRAMEWORK

Every agent must have automated evaluation suites.

## Persona Tests

Does the agent behave according to its role?

## Capability Tests

Can it perform its assigned tasks?

## Boundary Tests

Does it refuse tasks outside its authority?

## Security Tests

Does it protect secrets and sensitive data?

## Collaboration Tests

Can it delegate and consume peer outputs correctly?

## Failure Tests

Does it escalate rather than hallucinate?

## Regression Tests

Does a prompt/model change alter expected behavior?

Create evaluation datasets and make them executable in CI.

---

# 27. REPOSITORY STRUCTURE

Conform to the specification's repository structure:

```text
gcp-landing-zone-ai/
├── README.md
├── MULTI_AGENT_TEAM_SPECIFICATION.md
├── AGENT_OPERATING_MODEL.md
├── CONTRIBUTING.md
├── SECURITY.md
│
├── docs/
│   ├── requirements/
│   ├── architecture/
│   ├── adr/
│   ├── security/
│   ├── finops/
│   ├── operations/
│   ├── testing/
│   └── runbooks/
│
├── agents/
│   ├── product_owner/
│   ├── project_manager/
│   ├── engineering_orchestrator/
│   ├── platform_architect/
│   ├── solution_architect/
│   ├── security_architect/
│   ├── devops/
│   │   ├── lead/
│   │   ├── infrastructure/
│   │   ├── cicd/
│   │   ├── sre/
│   │   └── finops/
│   ├── development/
│   │   ├── lead/
│   │   ├── frontend/
│   │   ├── backend/
│   │   ├── integration/
│   │   └── ai_automation/
│   ├── testing/
│   │   ├── lead/
│   │   ├── automation/
│   │   └── nfr/
│   └── application_management/
│       ├── lead/
│       ├── support/
│       └── reliability/
│
├── orchestration/
│   ├── workflows/
│   ├── task_graphs/
│   ├── routing/
│   ├── policies/
│   └── state/
│
├── tools/
│   ├── gcp/
│   ├── terraform/
│   ├── git/
│   ├── cicd/
│   ├── testing/
│   ├── security/
│   └── finops/
│
├── memory/
│   ├── schemas/
│   ├── project/
│   ├── organization/
│   └── episodic/
│
├── policies/
│   ├── agent_permissions.yaml
│   ├── security_policy.yaml
│   ├── deployment_policy.yaml
│   ├── approval_policy.yaml
│   └── data_policy.yaml
│
├── infrastructure/
│   ├── terraform/
│   ├── modules/
│   └── environments/
│
├── applications/
│   ├── frontend/
│   ├── backend/
│   └── integration/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── performance/
│   └── security/
│
└── .github/
    └── workflows/
```

---

# 28. CONFIGURATION AND SECRETS

Never hard-code:

- `NVIDIA_API_KEY`
- database passwords
- GCP service account credentials
- API tokens
- production secrets

Use environment/configuration.

Provide:

```text
.env.example
```

containing placeholders only.

Example:

```text
NVIDIA_API_KEY=nvapi-REPLACE_ME

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agent_memory
POSTGRES_USER=agent_admin
POSTGRES_PASSWORD=CHANGE_ME

OLLAMA_LOCAL_URL=http://...
OLLAMA_REMOTE_URL=http://...
```

Never commit real credentials.

---

# 29. DATABASE MIGRATIONS

Implement migration support for PostgreSQL.

At minimum define tables/entities for:

```text
agents
agent_contracts
tasks
task_dependencies
agent_messages
evidence
collaboration_requests
reviews
quality_gates
approvals
audit_events
agent_memory
project_memory
model_executions
tool_executions
workflow_runs
cost_records
evaluation_results
```

Use migrations rather than creating schema implicitly during application
startup.

---

# 30. END-TO-END PILOT

The first production-oriented pilot should be deliberately smaller than a
full Landing Zone deployment.

Implement:

> Provision a new non-production GCP application environment using the
> approved Landing Zone.

The workflow should demonstrate:

```text
Product Owner
      |
Project Manager
      |
Engineering Orchestrator
      |
Platform Architect
      |
Solution Architect
      |
Security Architect
      |
FinOps
      |
DevOps
      |
Development
      |
Testing
      |
Application Management
      |
Quality Gates
      |
Approval
      |
Provision
      |
Validate
      |
Operations Readiness
```

The pilot MUST be capable of running with deterministic mock/local tools
before production GCP credentials are introduced.

---

# 31. FULL GCP LANDING ZONE WORKFLOW

After the pilot succeeds, implement the larger workflow:

> Design and implement a production-ready GCP Landing Zone.

It must cover:

1. requirements
2. organization hierarchy
3. folders/projects
4. IAM
5. networking
6. shared services
7. security
8. logging
9. monitoring
10. policy controls
11. Terraform
12. CI/CD
13. FinOps
14. testing
15. operational readiness
16. peer review
17. quality gates
18. human approval
19. release
20. validation
21. documentation
22. knowledge capture

---

# 32. NO FALSE SUCCESS

Never report:

```text
COMPLETED
```

unless Definition of Done passes.

Never report:

```text
APPROVED
```

unless an authorized reviewer or human approval exists.

Never report:

```text
VALIDATED
```

without validation evidence.

Never report:

```text
DEPLOYED
```

unless the deployment operation actually succeeded.

Never create fake evidence.

Never silently skip failed tasks.

---

# 33. TESTING REQUIREMENTS

## Unit Tests

Test:

- contracts
- registry
- task lifecycle
- dependency resolution
- evidence
- collaboration
- peer review
- SoD
- approvals
- tools
- model routing
- memory
- audit
- state transitions

## Integration Tests

Test:

- orchestrator -> agent
- agent -> model
- agent -> tool
- tool -> evidence
- agent -> peer review
- review -> gate
- gate -> approval
- approval -> deployment
- deployment -> validation
- failure -> escalation

## AI Governance Tests

Test:

- prompt injection
- tool abuse
- authority boundary
- secret leakage
- sensitive-data leakage
- hallucinated evidence
- fabricated tool results
- unauthorized deployment
- unauthorized IAM change

## E2E Tests

Test the complete non-production pilot.

## Negative Tests

Explicitly test:

- missing evidence
- failed security review
- missing approval
- unauthorized tool
- invalid agent
- dependency failure
- SoD violation
- model outage
- NVIDIA endpoint failure
- Ollama fallback
- PostgreSQL outage
- tool failure
- rollback

---

# 34. DEFINITION OF DONE

The implementation is NOT complete until all of the following are true:

- [ ] All 22 agents are initialized
- [ ] No registry entry is `None`
- [ ] Every agent has a valid contract
- [ ] Every agent has capabilities
- [ ] Every agent has memory
- [ ] Every agent has authorized tools
- [ ] Model registry is operational
- [ ] NVIDIA model routing is operational
- [ ] Ollama fallback is operational
- [ ] PostgreSQL persistence is operational
- [ ] Task graph is operational
- [ ] Dependency blocking works
- [ ] Evidence registry works
- [ ] Tool outputs become evidence
- [ ] Peer reviews execute
- [ ] Review rejection blocks work
- [ ] SoD enforcement executes
- [ ] SoD violations block work
- [ ] Quality gates execute
- [ ] Failed gates block work
- [ ] Human approval blocks sensitive operations
- [ ] Memory is persisted
- [ ] Audit trail is persisted
- [ ] Observability metrics exist
- [ ] Model usage/cost is tracked
- [ ] Agent evaluation framework exists
- [ ] Prompt injection tests exist
- [ ] Security boundary tests exist
- [ ] Non-production pilot succeeds
- [ ] Full Landing Zone workflow is executable
- [ ] Negative tests pass
- [ ] `pytest` passes
- [ ] `ruff check .` passes
- [ ] migrations work
- [ ] documentation is updated
- [ ] no fake completion/evidence exists

---

# 35. IMPLEMENTATION ORDER

Execute in this order:

## Phase 0 — Repository Assessment

Inspect the entire repository and compare it against:

```text
MULTI_AGENT_TEAM_SPECIFICATION.md
```

Produce:

```text
docs/IMPLEMENTATION_ASSESSMENT.md
```

## Phase 1 — Contracts and Registry

Implement:

- agent contracts
- registry
- validation
- AgentFactory

## Phase 2 — PostgreSQL Foundation

Implement:

- database configuration
- migrations
- repositories
- persistence interfaces

## Phase 3 — Model Infrastructure

Implement:

- model registry
- model router
- NVIDIA provider
- Ollama provider
- health checks
- fallback routing
- model execution records

## Phase 4 — Task Engine

Implement:

- task schema
- dependency graph
- state machine
- retries
- failure handling

## Phase 5 — Evidence

Implement:

- EvidenceRegistry
- ToolResult
- evidence validation
- provenance

## Phase 6 — Tools

Implement:

- ToolRegistry
- authorization
- GCP adapters
- Terraform adapters
- Git
- testing
- security
- FinOps
- observability

## Phase 7 — Collaboration

Implement:

- agent messaging
- peer review
- collaboration evidence
- review enforcement

## Phase 8 — Governance

Implement:

- SoD
- quality gates
- security gates
- approval gates
- ADR governance

## Phase 9 — Memory

Implement:

- agent memory
- project memory
- organization memory
- episodic memory
- semantic/vector memory

## Phase 10 — Observability and Audit

Implement:

- structured logging
- metrics
- tracing
- audit trail
- cost tracking

## Phase 11 — Agent Implementation

Implement all 22 agents according to their contracts and personas.

## Phase 12 — Pilot

Implement and pass:

> Provision a new non-production GCP application environment using the
> approved Landing Zone.

## Phase 13 — Full Workflow

Implement:

> Design and implement a production-ready GCP Landing Zone.

## Phase 14 — Evaluation

Implement persona, capability, boundary, security, collaboration, failure,
and regression tests.

## Phase 15 — Production Readiness

Run:

```bash
ruff check .
pytest -q
```

and all integration/e2e tests.

Do not claim completion if any mandatory test or gate fails.

---

# 36. REPOSITORY INSPECTION REQUIREMENT

Before modifying code:

1. inspect the complete repository
2. read `MULTI_AGENT_TEAM_SPECIFICATION.md`
3. inspect `base.py`
4. inspect `collaboration.py`
5. inspect `contracts.py`
6. inspect `engine.py`
7. inspect all agents
8. inspect orchestration
9. inspect tools
10. inspect configuration
11. inspect database/migrations
12. inspect tests
13. inspect `config/models.yaml`
14. inspect existing bootstrap scripts
15. identify working code
16. identify broken/stub code

Do not overwrite good existing implementation unnecessarily.

---

# 37. REQUIRED DELIVERABLES

Deliver:

1. 22 fully initialized agents
2. AgentFactory
3. validated AgentRegistry
4. complete contracts
5. operational orchestrator
6. dependency-aware task engine
7. evidence registry
8. tool registry
9. tool authorization
10. model registry
11. NVIDIA provider
12. Ollama fallback provider
13. PostgreSQL persistence
14. memory architecture
15. collaboration engine
16. peer review
17. SoD enforcement
18. quality gates
19. human approval
20. audit trail
21. observability
22. cost tracking
23. evaluation framework
24. non-production pilot
25. full Landing Zone workflow
26. unit tests
27. integration tests
28. security tests
29. AI governance tests
30. E2E tests
31. migrations
32. `.env.example`
33. updated README
34. `docs/IMPLEMENTATION_ASSESSMENT.md`

---

# 38. IMPLEMENTATION REPORT

When finished, provide an implementation report containing:

1. Current implementation maturity
2. Architecture implemented
3. Agents implemented
4. Files created
5. Files modified
6. Database schema/migrations
7. Model routing
8. NVIDIA integration
9. Ollama fallback
10. Tool authorization
11. Evidence architecture
12. Collaboration
13. Peer review
14. SoD
15. Quality gates
16. Human approval
17. Memory
18. Audit
19. Observability
20. Cost tracking
21. Evaluation framework
22. Pilot results
23. E2E results
24. Test results
25. Known limitations
26. Exact commands to run the system

If anything remains incomplete, explicitly list it.

Do NOT claim 100% completion unless every mandatory acceptance criterion has
been verified by executable tests.

---

# 39. START NOW

**Do not merely describe what should be done.**

First inspect the repository.

Then compare the implementation against the authoritative specification.

Then implement the missing functionality incrementally.

Use the existing architecture where sound.

Make actual code changes.

Run tests.

Fix failures.

Run the non-production pilot.

Then run the full E2E workflow.

Only after verification provide the implementation report.

**MAKE THE CODE CHANGES.**
