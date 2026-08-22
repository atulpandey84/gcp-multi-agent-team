---
status: proposed
date: 2026-08-22
title: "ADR - Agent: product_owner"
owner: product_owner
---

Context
-------
The `product_owner` agent encapsulates product vision, business prioritization, and acceptance criteria for work produced by the multi-agent organization.

Decision
--------
Implement `product_owner` as a read-only evidence-driven agent that produces prioritized acceptance criteria and signoff artifacts. All production-impacting decisions require explicit human approval.

Consequences
------------
- Produces artifact: `product_requirements.yml` and acceptance criteria embedded in task outputs.
- Will not perform deploys or privileged infra changes.
