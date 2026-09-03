# GCP Multi-Agent Engineering Team

**A fully autonomous 22-agent engineering organization for GCP Landing Zone design, implementation, security, testing, deployment, and operations.**

Powered by **LangGraph + NVIDIA models** | **Human-in-the-loop governance** | **Enterprise-grade safety controls**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
- [Agent Organization](#agent-organization)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Safety & Governance](#safety--governance)
- [Monitoring & Operations](#monitoring--operations)
- [Testing](#testing)
- [Architecture & Design](#architecture--design)
- [Next Steps & Roadmap](#next-steps--roadmap)
- [Contributing](#contributing)
- [Documentation](#documentation)

---

## Overview

The **GCP Multi-Agent Engineering Team** is an enterprise-grade orchestration framework that deploys 22 specialized AI agents organized into functional teams:

- **Product & Delivery** (2 agents)
- **Architecture & Design** (3 agents)
- **DevOps & Infrastructure** (5 agents)
- **Development** (5 agents)
- **Testing & Quality** (3 agents)
- **Application Management & Reliability** (3 agents)
- **Engineering Governance** (1 agent)

This system models a real engineering organization where each agent has:
- **Bounded mission**: Clear responsibilities
- **Explicit authority**: Defined permissions and limitations
- **Specialized tools**: Role-specific capabilities
- **Institutional memory**: Persistent learning and decision history
- **Structured workflows**: Proven collaboration patterns
- **Quality gates**: Measurable completion criteria
- **Escalation paths**: Clear approval boundaries

**Use cases:**
- Automated GCP Landing Zone design and implementation
- Compliance and security posture assessment
- Infrastructure as Code (Terraform) generation and deployment
- Test automation and quality assurance
- Production operations and incident response
- Cost optimization (FinOps)
- Architectural decision-making with human oversight

---

## Core Capabilities

### 1. **Architecture & Design**
- Enterprise GCP Landing Zone design aligned with Google Cloud best practices
- Multi-cloud integration patterns
- Security architecture with threat modeling
- Solution trade-off analysis
- ADR (Architecture Decision Record) generation

### 2. **Infrastructure & DevOps**
- Terraform code generation and validation
- GCP infrastructure provisioning (with human approval)
- CI/CD pipeline orchestration
- Container and Kubernetes orchestration
- Infrastructure cost optimization and reporting

### 3. **Application Development**
- Full-stack application design
- Frontend and backend implementation
- API integration and testing
- Automation and AI/ML workflows
- Code review and quality enforcement

### 4. **Testing & Quality**
- Test strategy and planning
- Automated test generation
- Performance and load testing
- Non-functional requirement validation
- Compliance and security testing

### 5. **Production Operations**
- SRE and observability
- Incident response and runbook generation
- Application lifecycle management
- Production support and escalation
- Reliability engineering

### 6. **Governance & Orchestration**
- Multi-agent workflow orchestration
- Approval routing and escalation
- Compliance enforcement
- Evidence-based decision making
- Audit trail and accountability

---

## Agent Organization

### 22-Agent Team Structure

#### **Product & Delivery (2 agents)**
| ID | Role | Mission |
|---|---|---|
| 01 | Product Owner | Own product vision, business value, scope, prioritization |
| 02 | Project Manager | Delivery coordination, planning, risk management |

#### **Architecture & Design (3 agents)**
| ID | Role | Mission |
|---|---|---|
| 04 | Platform Architect | Platform architecture and design |
| 05 | Solution Architect | Solution-level architecture and trade-offs |
| 06 | Security Architect | Security design and reviews |

#### **DevOps & Infrastructure (5 agents)**
| ID | Role | Mission |
|---|---|---|
| 07 | DevOps Lead | DevOps strategy and CI/CD |
| 08 | Cloud Infrastructure Engineer | Cloud infra implementation |
| 09 | CI/CD Engineer | Pipelines and automation |
| 10 | SRE / Observability Engineer | SRE and telemetry |
| 11 | FinOps Engineer | Cost control and reporting |

#### **Development (5 agents)**
| ID | Role | Mission |
|---|---|---|
| 12 | Development Lead | Development delivery |
| 13 | Frontend Engineer | Frontend implementation |
| 14 | Backend Engineer | Backend implementation |
| 15 | Integration Engineer | System integration |
| 16 | AI / Automation Engineer | Automation and agents |

#### **Testing & Quality (3 agents)**
| ID | Role | Mission |
|---|---|---|
| 17 | QA Lead | Quality assurance |
| 18 | Test Automation Engineer | Test automation |
| 19 | Non-Functional Test Engineer | Performance and reliability testing |

#### **Application Management & Reliability (3 agents)**
| ID | Role | Mission |
|---|---|---|
| 20 | Application Management Lead | Application lifecycle management |
| 21 | L2/L3 Application Support Engineer | Support and incident handling |
| 22 | Production Reliability Engineer | Production reliability and runbooks |

#### **Engineering Governance (1 agent)**
| ID | Role | Mission |
|---|---|---|
| 03 | Engineering Orchestrator | Orchestrate engineering workflows and approvals |

---

## Technology Stack

### Core Framework
- **LangGraph** - Agentic workflow orchestration
- **LangChain** - LLM abstractions and tools
- **Pydantic** - Data validation and settings
- **PostgreSQL** - Persistent state and memory
- **FastAPI** - Monitoring and control UI
- **Uvicorn** - ASGI server

### AI/ML Models (NVIDIA)
- **Nemotron Ultra** - Critical architecture/orchestration
- **Nemotron Super** - Senior reasoning tasks
- **DeepSeek V4 Pro** - Coding/implementation
- **Nemotron Lightning** - Fast routine work
- **DeepSeek V4 Flash** - Fast coding operations
- **Nemotron Embed/Rerank** - RAG and semantic search

### Infrastructure & Tools
- **GCP (Google Cloud Platform)** - Target deployment environment
- **Terraform** - Infrastructure as Code
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **pytest** - Testing framework

### Developer Experience
- **Ruff** - Code linting and formatting
- **mypy** - Type checking
- **GNU Make** - Build automation
- **Python 3.11+** - Programming language

---

## Prerequisites

### System Requirements
- **Python 3.11+** (verify with `python --version`)
- **Git** for version control
- **Docker** (optional, for PostgreSQL via Docker Compose)
- **PostgreSQL 13+** (if not using Docker)
- **2GB+ RAM** for the virtual environment
- **Internet connectivity** for NVIDIA API and GCP

### API Keys & Credentials
- **NVIDIA_API_KEY** - For NVIDIA model access (register at [nvidia.com/build](https://build.nvidia.com))
- **GCP Service Account** - For infrastructure provisioning (download JSON key)
- **MONITORING_API_KEY** - For the monitoring UI (any secure string)

### Recommended Tools
- **GNU Make** - Build automation
- **PostgreSQL CLI** (`psql`) - Database debugging
- **gcloud CLI** - GCP utilities
- **Terraform CLI** - Infrastructure validation (optional)

---

## Quick Start

### 1. Clone and Setup Environment

**Linux/macOS:**
```bash
git clone <repository-url>
cd gcp-multi-agent-team
cp .env.example .env
./scripts/bootstrap.sh
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
git clone <repository-url>
cd gcp-multi-agent-team
Copy-Item .env.example .env
.\scripts\bootstrap.ps1
.\.venv\Scripts\Activate.ps1
```

### 2. Configure API Keys

Edit `.env`:
```bash
NVIDIA_API_KEY=your-nvidia-api-key-here
MONITORING_API_KEY=your-secure-monitoring-key
DATABASE_URL=postgresql://user:password@localhost:5432/multi_agent_team
```

### 3. Verify Installation

```bash
# Run tests
make test

# Lint code
make lint
```

### 4. Start PostgreSQL (if using Docker)

```bash
docker-compose up -d postgres
```

### 5. Run the System

```bash
# Using Make
make run

# Or directly
export PYTHONPATH=src
python -m multi_agent_team.main
```

---

## Configuration

### Environment Variables

**Required:**
- `NVIDIA_API_KEY` - NVIDIA API key for model access
- `MONITORING_API_KEY` - Secret key for monitoring UI access

**Optional:**
- `DATABASE_URL` - PostgreSQL connection string (default: local SQLite)
- `MONITORING_DATABASE_URL` - Separate DB for monitoring (default: uses DATABASE_URL)
- `LOG_LEVEL` - Logging verbosity (default: INFO)

### Model Configuration

Edit [config/models.yaml](config/models.yaml) to configure model routing:

```yaml
models:
  - name: nemotron-ultra
    provider: nvidia
    deployment: critical-architecture
  - name: deepseek-v4-pro
    provider: nvidia
    deployment: coding
```

### Agent Configuration

Edit [config/agents.yaml](config/agents.yaml) to configure agents, tools, and permissions.

### Tool Permissions

Edit [config/tools.yaml](config/tools.yaml) to define which agents can invoke which tools.

### Policy Enforcement

Edit [config/policies.yaml](config/policies.yaml) to set governance rules.

---

## Running the System

### Command Line Interface

**Using Make (recommended):**
```bash
# Bootstrap environment
make bootstrap

# Install dependencies
make install

# Run tests
make test

# Run linter
make lint

# Start the system
make run

# Database operations
make compose-up          # Start PostgreSQL
make compose-down        # Stop PostgreSQL
make migrate-alembic     # Run migrations
```

**Direct Python:**
```bash
export PYTHONPATH=src
python -m multi_agent_team.main
```

### Monitoring UI

The system includes a lightweight FastAPI-based monitoring UI for real-time agent control and workflow tracking.

**Start the UI:**
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Set API key
export MONITORING_API_KEY=your-secure-key

# Run the UI
uvicorn src.multi_agent_team.monitoring.app:app --host 0.0.0.0 --port 8000
```

**Access the UI:**
- Open [http://localhost:8000](http://localhost:8000) in your browser
- Authenticate with your MONITORING_API_KEY
- View agent status, workflows, and telemetry
- Control and approve agent actions

---

## Project Structure

```
gcp-multi-agent-team/
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── config/                           # Configuration files
│   ├── agents.yaml                   # Agent definitions
│   ├── agents_contracts.yaml         # Agent input/output contracts
│   ├── models.yaml                   # Model routing
│   ├── tools.yaml                    # Tool permissions
│   ├── policies.yaml                 # Governance policies
│   └── agents_artifacts/             # Agent-specific artifacts
│       ├── platform_architect/
│       ├── security_architect/
│       ├── backend_engineer/
│       ├── test_automation_engineer/
│       └── ... (20 more agents)
├── data/                             # Runtime data
│   └── workflows/                    # Workflow execution history
├── docs/                             # Documentation
│   ├── adr/                          # Architecture Decision Records
│   └── operations/                   # Operational runbooks
├── scripts/                          # Bootstrap and utility scripts
│   ├── bootstrap.sh                  # Linux/macOS setup
│   ├── bootstrap.ps1                 # Windows setup
│   └── bootstrap.py                  # Python setup utilities
├── src/multi_agent_team/             # Main application
│   ├── main.py                       # Entry point
│   ├── agents/                       # Agent implementations
│   ├── tools/                        # Tool implementations
│   ├── workflows/                    # LangGraph workflow definitions
│   ├── memory/                       # Agent memory systems
│   ├── models/                       # Data models
│   ├── monitoring/                   # Monitoring UI and telemetry
│   └── config/                       # Runtime configuration
├── tests/                            # Test suite
│   ├── test_smoke.py
│   ├── test_workflow_runtime.py
│   ├── test_governance_and_specialized_agents.py
│   ├── test_compliance.py
│   └── ... (more tests)
├── pyproject.toml                    # Python project metadata
├── requirements.txt                  # Python dependencies
├── Makefile                          # Build automation
├── Dockerfile                        # Docker image
├── docker-compose.yml                # Docker Compose for PostgreSQL
├── alembic.ini                       # Alembic configuration
├── MULTI_AGENT_TEAM_SPECIFICATION.md # Authoritative specification
└── README.md                         # This file
```

---

## Development Workflow

### 1. **Create Feature Branch**
```bash
git checkout -b feature/agent-enhancement
```

### 2. **Make Changes**
- Update agent prompts in [config/agents.yaml](config/agents.yaml)
- Add tools in [config/tools.yaml](config/tools.yaml)
- Modify agent implementation in [src/multi_agent_team/agents/](src/multi_agent_team/agents/)

### 3. **Test Locally**
```bash
make test          # Run full test suite
make lint          # Check code style
pytest -v          # Verbose testing
```

### 4. **Validate Changes**
- Verify agent contracts match inputs/outputs in [config/agents_contracts.yaml](config/agents_contracts.yaml)
- Check tool permissions in [config/tools.yaml](config/tools.yaml)
- Review governance policies in [config/policies.yaml](config/policies.yaml)

### 5. **Run System Integration Test**
```bash
make run
```

### 6. **Commit and Push**
```bash
git add .
git commit -m "feat: enhance agent-id with new capability"
git push origin feature/agent-enhancement
```

### 7. **Create Pull Request**
- Include specification alignment
- Add test evidence
- Document breaking changes

---

## Safety & Governance

### Core Safety Principles

The system implements a **fail-closed** architecture where dangerous operations require explicit human approval:

#### Disabled by Default
- ✅ GCP infrastructure mutations
- ✅ Terraform apply operations
- ✅ Production deployment
- ✅ Database destruction
- ✅ IAM privilege escalation
- ✅ Organization-level policy changes

#### Human-in-the-Loop Required
The following actions trigger escalation to humans for approval:
- Production database changes
- Production networking changes with blast radius
- Major architecture exceptions
- Unbudgeted material cloud expenditure
- Security or compliance exceptions
- External communication representing the organization

#### Authorization Framework
Implement tool authorization by:

1. **Enable specific tools** in [config/tools.yaml](config/tools.yaml):
```yaml
tools:
  terraform_apply:
    enabled: false              # Disabled by default
    requires_approval: true
    approval_chain: [platform_architect, devops_lead]
```

2. **Implement approval handler** in tool implementation:
```python
if tool.requires_approval:
    approval = await request_human_approval(
        agent=current_agent,
        action=tool.name,
        context=tool.input,
        approval_chain=tool.approval_chain
    )
    if approval.status != ApprovalStatus.APPROVED:
        raise ToolExecutionBlocked(f"Approval denied: {approval.reason}")
```

3. **Audit all actions** in [data/workflows/](data/workflows/):
```json
{
  "workflow_id": "...",
  "agent": "devops_lead",
  "action": "terraform_apply",
  "approval": {
    "requested_at": "2026-01-15T10:00:00Z",
    "approved_by": "platform_architect",
    "approval_chain": ["platform_architect", "engineering_orchestrator"],
    "status": "approved"
  },
  "executed_at": "2026-01-15T10:05:00Z"
}
```

### Governance Policies

Review [config/policies.yaml](config/policies.yaml) for:
- Separation of duties
- Escalation rules
- Approval workflows
- Audit requirements
- Quality gates
- Definition of Done

---

## Monitoring & Operations

### Real-Time Monitoring UI

The FastAPI-based monitoring UI provides:
- **Agent Status Dashboard** - Current state of all 22 agents
- **Workflow Tracker** - Real-time workflow execution status
- **Telemetry & Metrics** - Agent performance and API usage
- **Audit Log** - Complete action history with approvals
- **Manual Controls** - Trigger workflows, approve actions, override decisions

**Start monitoring:**
```bash
export MONITORING_API_KEY=your-key
uvicorn src.multi_agent_team.monitoring.app:app --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

### Agent Memory & Persistence

Agents maintain institutional memory through:
- **LangGraph checkpoints** - Workflow execution state
- **PostgreSQL storage** - Persistent decision history
- **Vector embeddings** - Semantic retrieval of past decisions
- **ADRs and artifacts** - Durable architecture decisions

Access memory:
```bash
# View agent memory
python -m src.multi_agent_team.memory list --agent=backend_engineer

# Query decision history
python -m src.multi_agent_team.memory query "recent security decisions"
```

### Operational Runbooks

Check [docs/operations/](docs/operations/) for runbooks on:
- Incident response
- Emergency scale-up
- Deployment rollback
- Cost anomalies
- Security incidents
- Agent failures

### Telemetry & Logging

Configure logging in `.env`:
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json  # or text
```

View logs:
```bash
# Recent logs
tail -100f logs/multi_agent_team.log

# Search logs
grep "backend_engineer" logs/multi_agent_team.log
```

---

## Testing

### Test Suite

Run all tests:
```bash
make test              # Quick test run
pytest -v             # Verbose output
pytest -s             # Show print statements
pytest --cov          # Coverage report
```

### Test Categories

**Smoke Tests** ([tests/test_smoke.py](tests/test_smoke.py))
- System startup
- Agent initialization
- Basic workflows

**Workflow Tests** ([tests/test_workflow_runtime.py](tests/test_workflow_runtime.py))
- Multi-agent orchestration
- Workflow execution
- State management

**Governance Tests** ([tests/test_governance_and_specialized_agents.py](tests/test_governance_and_specialized_agents.py))
- Separation of duties
- Approval workflows
- Policy enforcement

**Compliance Tests** ([tests/test_compliance.py](tests/test_compliance.py))
- Security requirements
- Audit trails
- Data protection

**Integration Tests** ([tests/test_dynamic_chat_and_persistence.py](tests/test_dynamic_chat_and_persistence.py))
- Agent collaboration
- Memory persistence
- Dynamic workflows

### Writing New Tests

```python
# tests/test_my_feature.py
import pytest
from multi_agent_team import Agent

@pytest.mark.asyncio
async def test_agent_decision_making():
    agent = Agent(role="backend_engineer")
    result = await agent.execute(task="design API endpoint")
    assert result.status == "complete"
    assert "design_artifact" in result.artifacts
```

---

## Architecture & Design

### Core Design Principles

**1. Agents are Autonomous Specialists**
- Each agent has bounded mission, explicit authority, and specialized tools
- Not generic chatbots; designed for specific responsibilities

**2. Separation of Duties**
- No single agent can design, implement, approve, and deploy the same high-risk change
- Independent review required for architecture, implementation, and validation

**3. Human-in-the-Loop for High-Risk Actions**
- Production destructive changes require human approval
- Security/compliance exceptions need escalation
- Major architecture decisions require stakeholder sign-off

**4. Evidence Over Assertions**
- Agents prefer repository evidence, tests, and runtime telemetry
- All assumptions explicitly labeled
- Decisions backed by artifacts and documentation

**5. Everything Important Becomes an Artifact**
- ADRs capture architectural decisions
- Terraform changes represent infrastructure intent
- Test results prove quality
- Incident reports drive learning

**6. Fail Closed**
- When insufficient information exists, agents escalate rather than invent
- Missing evidence triggers human review, not assumptions

### LangGraph Workflow Architecture

The system uses **LangGraph** for workflow orchestration:

```
Input → Routing → Agent Teams → Decision → Escalation → Output
         |            |           |         |             |
    orchestrator   specialists   logic    approval       result
```

### Memory Architecture

Three-tier memory system:
- **Workflow-level**: Execution checkpoints (ephemeral)
- **Agent-level**: Decision history (persistent, PostgreSQL)
- **Organization-level**: ADRs and policies (durable artifacts)

See [MULTI_AGENT_TEAM_SPECIFICATION.md](MULTI_AGENT_TEAM_SPECIFICATION.md#memory-architecture) for details.

---

## Next Steps & Roadmap

### Phase 1: Foundation (In Progress)
- [x] Core 22-agent framework
- [x] LangGraph orchestration
- [x] NVIDIA model routing
- [x] Basic tool implementations
- [x] **TODO:** Complete all agent system prompts
- [x] **TODO:** Implement all specialized tools per agent role

### Phase 2: Governance & Safety (Upcoming)
- [ ] Human approval workflows for high-risk actions
- [ ] Complete audit trail implementation
- [ ] Policy enforcement engine
- [ ] Compliance testing framework
- [ ] Security architecture review

### Phase 3: Production Readiness (Planned)
- [ ] Full Terraform provider for GCP
- [ ] Advanced memory and learning system
- [ ] Multi-tenant support
- [ ] High-availability deployment
- [ ] Cost optimization automation
- [ ] Automated SLO enforcement

### Phase 4: Advanced Features (Future)
- [ ] Multi-cloud support (AWS, Azure)
- [ ] Agent fine-tuning on organization data
- [ ] Advanced reasoning with chain-of-thought
- [ ] Continuous improvement through feedback loops
- [ ] Integration with existing ITSM systems
- [ ] AI-assisted capacity planning

### Critical TODOs

#### Immediate (This Sprint)
1. ~~Complete agent system prompts in [config/agents_artifacts/](config/agents_artifacts/) (20/22 remaining)~~ **✅ COMPLETED - All 22 system prompts created**
2. ~~Implement tool authorization in [config/tools.yaml](config/tools.yaml)~~ **✅ COMPLETED - 42 tools configured with permissions**
3. Add human approval handler to orchestration layer
4. Complete Terraform provider interface

#### Short Term (Next 2 Weeks)
1. Deploy monitoring UI to staging environment
2. Run governance and compliance test suite
3. Document approval workflows in [docs/operations/](docs/operations/)
4. Implement advanced memory queries
5. Add cost anomaly detection

#### Medium Term (Next Month)
1. Complete multi-cloud provider support
2. Implement automated SLO enforcement
3. Build agent fine-tuning pipeline
4. Create incident response automation
5. Deploy to production (GCP Landing Zone)

---

### ⚠️ Areas for Review & Improvement (Potential Pain Points)

1.  **API Definition (`api/`, `schemas/`):**
    *   **Review:** Ensure that every cross-module communication point uses classes defined in `schemas/`. This prevents runtime type errors when agents talk to each other or call external APIs.
    *   **Suggestion:** Standardize on Pydantic models (if using FastAPI/Pydantic) for all request/response contracts across *all* modules, not just the API layer.

2.  **Agent Implementation (`agents/`):**
    *   **Review:** How do agents receive their "intent"? Does an agent pull from a queue, or is it passed directly via the `orchestration/` layer?
    *   **Suggestion:** Consider giving each primary agent class a clear **role definition** (e.g., `AgentRole(Enum)`) to prevent ambiguity when multiple agents claim responsibility for the same task.

3.  **State Management & Context (`memory/`, `governance/`):**
    *   **Review:** How is context managed? Is it a single global store, or does the `orchestration/` layer manage per-session contexts passed to memory services?
    *   **Suggestion:** Explicitly document how session boundaries are maintained. The combination of `memory/` and the database via Alembic needs to be tightly linked here.

4.  **Execution Flow (`main.py`, `demo/`):**
    *   The separation between `demo/` (examples) and `main.py` (entry point) is good.
    *   **Suggestion:** The `main.py` entry point should ideally bootstrap the *entire* system stack (DB connection, session manager, initial cache) before calling a function within `orchestration/`.

### 🗄️ Database Layer Review (`alembic/`)

The presence of an Alembic structure confirms that state persistence is planned.

*   **Review:** The models referenced by these migrations must accurately capture the necessary state for *all* components: Agent profiles, Chat History (Memory), Tool usage logs, and Orchestration metadata.
*   **Action:** Verify that the `models/` directory under `src/...` contains corresponding SQLAlchemy/ORM mappings that correspond to the tables defined in Alembic.

---

## 🚀 Actionable Plan Summary

| Priority | Area | Recommendation | Rationale |
| :--- | :--- | :--- | :--- |
| **High** | **Interface Contracts** | Enforce usage of `schemas/` types for *all* internal function calls, not just API endpoints. | Prevents integration bugs between modules like `agents` and `orchestration`. |
| **Medium** | **Workflow Tracing** | Create a diagram or doc outlining the flow: User Input $\rightarrow$ Orchestrator $\rightarrow$ Agent Call $\rightarrow$ Tool Execution $\rightarrow$ Memory Update $\rightarrow$ Final Output. | Validates that all complex pieces fit together correctly. |
| **Medium** | **Initialization Logic** | Review `main.py` to ensure it handles dependency injection (DI) for services like the database connection or caching layer before calling workflows. | Ensures modules run in a controlled, initialized state. |
| **Low** | **Documentation** | Update the README to reflect the *internal* module interactions clearly, referencing this breakdown. | Helps future developers onboard quickly. |

---

## Model Policy

### Model Assignment by Task

| Model | Tier | Use Case | Max Tokens |
|---|---|---|---|
| Nemotron Ultra | Critical | Architecture decisions, orchestration, high-stakes reasoning | 4096 |
| Nemotron Super | Senior | Complex analysis, design review, senior decision-making | 4096 |
| DeepSeek V4 Pro | Standard | Code implementation, technical design, detailed planning | 8192 |
| Nemotron Lightning | Fast | Routine operations, status checks, simple tasks | 2048 |
| DeepSeek V4 Flash | Ultra-Fast | Quick analysis, formatting, data preparation | 1024 |
| Nemotron Embed/Rerank | Semantic | RAG retrieval, document ranking, semantic search | N/A |

### Configuration

Update model routing in [config/models.yaml](config/models.yaml):

```yaml
models_active:
  architecture_decisions: nemotron-ultra
  senior_reasoning: nemotron-super
  implementation: deepseek-v4-pro
  routine_work: nemotron-lightning
  fast_coding: deepseek-v4-flash
  rag_retrieval: nemotron-embed
```

**Production Requirement:** Verify exact model identifiers against the current [NVIDIA Build catalog](https://build.nvidia.com) before deploying to production.

---

## Contributing

### Code Standards

- **Python 3.11+** syntax
- **Type hints** required for all functions
- **Docstrings** for all classes and public methods
- **PEP 8** compliance (enforced via Ruff)
- **pytest** coverage target: 80%+

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

Closes #<issue-number>
```

**Types:** feat, fix, docs, test, refactor, chore
**Scope:** agent-id or component (e.g., `feat(backend_engineer): add API validation`)

### Pull Request Process

1. Create feature branch
2. Make changes and test locally
3. Update documentation
4. Ensure all tests pass: `make test`
5. Run linter: `make lint`
6. Create PR with specification alignment
7. Request review from relevant agents' owners
8. Address feedback
9. Merge when approved

---

## Documentation

### Key Documents

| Document | Purpose |
|---|---|
| [MULTI_AGENT_TEAM_SPECIFICATION.md](MULTI_AGENT_TEAM_SPECIFICATION.md) | Authoritative specification for agent organization, governance, tools, and workflows |
| [IMPLEMENT_22_AGENT_ORGANIZATION_PROMPT_ENHANCED.md](IMPLEMENT_22_AGENT_ORGANIZATION_PROMPT_ENHANCED.md) | Implementation roadmap and current priorities |
| [docs/adr/](docs/adr/) | Architecture Decision Records for design decisions |
| [docs/operations/](docs/operations/) | Operational runbooks for production management |
| [config/agents.yaml](config/agents.yaml) | Agent definitions and missions |
| [config/agents_contracts.yaml](config/agents_contracts.yaml) | Input/output contracts for each agent |
| [config/tools.yaml](config/tools.yaml) | Tool definitions and permissions |
| [config/policies.yaml](config/policies.yaml) | Governance policies and approval workflows |

### Agent-Specific Documentation

Each agent has an artifact folder in [config/agents_artifacts/](config/agents_artifacts/):

```
config/agents_artifacts/
├── platform_architect/
│   ├── system_prompt.md
│   ├── tools.yaml
│   ├── examples/
│   └── guidelines.md
├── backend_engineer/
│   ├── system_prompt.md
│   ├── tools.yaml
│   └── coding_standards.md
└── ... (20 more agents)
```

---

## Troubleshooting

### Common Issues

**Issue:** NVIDIA_API_KEY not recognized
```bash
# Solution: Verify .env file
grep NVIDIA_API_KEY .env
echo $NVIDIA_API_KEY  # Should print your key
```

**Issue:** PostgreSQL connection failed
```bash
# Solution: Start Docker containers
docker-compose up -d postgres
# Wait 10 seconds for startup
sleep 10
make migrate-alembic
```

**Issue:** Tests failing
```bash
# Solution: Run with verbose output
pytest -v -s
# Check Python version
python --version  # Must be 3.11+
```

**Issue:** Monitoring UI not accessible
```bash
# Solution: Verify port and API key
curl -H "Authorization: Bearer your-key" http://localhost:8000/api/health
```

### Getting Help

- Check [MULTI_AGENT_TEAM_SPECIFICATION.md](MULTI_AGENT_TEAM_SPECIFICATION.md) for authoritative guidance
- Review [docs/operations/](docs/operations/) for operational issues
- Inspect agent logs: `tail -100f logs/multi_agent_team.log`
- Search issue tracker for similar problems
- Contact the engineering team lead

---

## License

Copyright © 2026. All rights reserved.

---

## Support & Contact

- **Engineering Lead:** See [config/agents.yaml](config/agents.yaml) for agent contacts
- **Architecture Questions:** Contact platform_architect or solution_architect
- **Security Issues:** Contact security_architect immediately
- **Production Incidents:** Trigger production_reliability_engineer agent

---

**Last Updated:** 2026-09-03  
**Status:** In Development (Phase 1/4)

