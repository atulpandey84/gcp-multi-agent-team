"""
Quality Gate Framework per Section 15 of MULTI_AGENT_TEAM_SPECIFICATION.md.
Implements blocking quality gates for security, testing, FinOps, and compliance.
"""

from typing import Any, Dict


def validate_quality_gates(gate_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce quality gate metrics.

    Returns a dict with keys:
        - passed: bool
        - reason: str
    """
    if gate_name == "security":
        critical_vulnerabilities = metrics.get("critical_vulnerabilities", 0)
        if critical_vulnerabilities > 0:
            return {
                "passed": False,
                "reason": f"Security quality gate failed: {critical_vulnerabilities} critical vulnerabilities found.",
            }
        return {"passed": True, "reason": "Security quality gate passed: no critical vulnerabilities."}

    elif gate_name == "testing":
        coverage = metrics.get("test_coverage", 0.0)
        if coverage < 80.0:
            return {
                "passed": False,
                "reason": f"Testing quality gate failed: coverage {coverage}% is below threshold 80.0%.",
            }
        return {"passed": True, "reason": f"Testing quality gate passed: coverage {coverage}% >= 80.0%."}

    elif gate_name == "finops":
        estimated_cost = metrics.get("monthly_cost", 0.0)
        budget_limit = metrics.get("budget_limit", 10000.0)
        if estimated_cost > budget_limit:
            return {
                "passed": False,
                "reason": f"FinOps quality gate failed: cost ${estimated_cost} exceeds budget limit ${budget_limit}.",
            }
        return {
            "passed": True,
            "reason": f"FinOps quality gate passed: cost ${estimated_cost} within budget ${budget_limit}.",
        }

    elif gate_name == "compliance":
        passed_controls = metrics.get("passed_controls", 0)
        total_controls = metrics.get("total_controls", 0)
        if total_controls > 0 and passed_controls < total_controls:
            return {
                "passed": False,
                "reason": f"Compliance quality gate failed: {passed_controls}/{total_controls} controls passed.",
            }
        return {"passed": True, "reason": "Compliance quality gate passed: all controls satisfied."}

    else:
        return {"passed": True, "reason": f"Quality gate '{gate_name}' passed (default)."}


def evaluate_gate_set(gate_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate a set of quality gates.

    Returns:
        dict with keys:
            - passed: bool (all gates passed)
            - failed: list of gate names that failed
            - results: dict of gate_name -> result
    """
    failed = []
    results = {}
    for gate_name, metrics in gate_metrics.items():
        result = validate_quality_gates(gate_name, metrics)
        results[gate_name] = result
        if not result["passed"]:
            failed.append(gate_name)

    return {
        "passed": len(failed) == 0,
        "failed": failed,
        "results": results,
    }
