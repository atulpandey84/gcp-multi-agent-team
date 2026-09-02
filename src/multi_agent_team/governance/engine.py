"""Governance engine with approval, quality-gate, and separation-of-duties checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class QualityGate:
    name: str
    passed: bool = False
    owner: str = "system"
    details: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class QualityGateSummary:
    gates: List[QualityGate] = field(default_factory=list)
    passed: bool = False
    failed: List[str] = field(default_factory=list)


class GovernanceEngine:
    """Central policy enforcement for SoD, approvals, and quality gates."""

    HIGH_RISK_ACTIONS = {
        "iam_policy_change",
        "terraform_apply",
        "production_deployment",
        "security_exception",
        "architecture_approval",
    }

    def __init__(self, *, allowed_actions: Optional[Iterable[str]] = None):
        self.allowed_actions = set(allowed_actions or [])

    def validate_separation_of_duties(self, author_id: str, reviewer_id: str, action_type: str) -> Dict[str, Any]:
        """Author cannot self-approve high-risk actions."""
        if action_type in self.HIGH_RISK_ACTIONS and author_id == reviewer_id:
            return {
                "allowed": False,
                "reason": f"Separation of Duties violation: Author '{author_id}' cannot self-approve action '{action_type}'.",
            }
        return {"allowed": True, "reason": "Separation of Duties check passed."}

    def requires_human_approval(self, risk: str, tool: Optional[str] = None) -> bool:
        if risk in {"high", "critical", "catastrophic"}:
            return True
        return tool in {"terraform_apply", "iam_policy_change", "project_delete", "production_deployment"}

    def validate_quality_gates(self, gate_name: str, metrics: Dict[str, Any]) -> QualityGate:
        """Enforce common project quality gates."""
        gate = QualityGate(name=gate_name, owner="governance_engine")

        if gate_name == "security":
            critical = int(metrics.get("critical_vulnerabilities", 0))
            gate.passed = critical == 0
            gate.details = {"critical_vulnerabilities": critical}
            gate.evidence = [f"security vulnerabilities: {critical}"]
            if not gate.passed:
                gate.details["reason"] = f"Security quality gate failed: {critical} critical vulnerabilities found."

        elif gate_name == "testing":
            coverage = float(metrics.get("test_coverage", 0.0))
            gate.passed = coverage >= 80.0
            gate.details = {"test_coverage": coverage}
            gate.evidence = [f"coverage={coverage}%"]
            if not gate.passed:
                gate.details["reason"] = f"Testing quality gate failed: coverage {coverage}% is below threshold 80.0%."

        elif gate_name == "finops":
            est_cost = float(metrics.get("monthly_cost", 0.0))
            budget = float(metrics.get("budget_limit", 10000.0))
            gate.passed = est_cost <= budget
            gate.details = {"monthly_cost": est_cost, "budget_limit": budget}
            gate.evidence = [f"monthly_cost=${est_cost}", f"budget_limit=${budget}"]
            if not gate.passed:
                gate.details["reason"] = f"FinOps quality gate failed: cost ${est_cost} exceeds budget limit ${budget}."

        else:
            gate.passed = True
            gate.details = dict(metrics)
            gate.evidence = ["default gate passed"]

        return gate

    def evaluate_gate_set(self, gate_metrics: Dict[str, Dict[str, Any]]) -> QualityGateSummary:
        gates: List[QualityGate] = []
        failed: List[str] = []
        for gate_name, metrics in gate_metrics.items():
            gate = self.validate_quality_gates(gate_name, metrics)
            gates.append(gate)
            if not gate.passed:
                failed.append(gate.name)

        return QualityGateSummary(gates=gates, passed=not failed, failed=failed)
