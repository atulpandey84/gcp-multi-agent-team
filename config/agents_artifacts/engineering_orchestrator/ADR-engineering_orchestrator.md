---
status: proposed
date: 2026-08-22
title: "ADR - Agent: engineering_orchestrator"
owner: engineering_orchestrator
---

Context
-------
The `engineering_orchestrator` agent coordinates workflows, composes tasks across agents, and sequences work.

Decision
--------
Implement as a workflow engine peer that emits structured plans and coordinates execution. All high-impact operations require human or designated-role approval.
