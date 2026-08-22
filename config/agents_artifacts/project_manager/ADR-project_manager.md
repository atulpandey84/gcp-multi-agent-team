---
status: proposed
date: 2026-08-22
title: "ADR - Agent: project_manager"
owner: project_manager
---

Context
-------
The `project_manager` agent coordinates delivery plans, milestones, and dependencies.

Decision
--------
Implement `project_manager` to emit plans, risk registers, and milestone artifacts. It cannot perform merges or deployments; those require human approval.

Consequences
------------
- Produces `release_plan.yml` and `risk_register.yaml` artifacts.
