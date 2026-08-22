---
status: proposed
date: 2026-08-22
title: "ADR - Agent: cloud_infrastructure_engineer"
owner: cloud_infrastructure_engineer
---

Context
-------
Implements cloud infra using IaC. Production changes require human approval and peer review.

Decision
--------
Agent emits Terraform plans and change-sets; applies only after human approvals and CI validation.
