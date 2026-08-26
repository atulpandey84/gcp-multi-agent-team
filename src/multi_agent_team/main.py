import argparse
import sys
import json
from .workflows.engineering import run
from .policies.engine import validate_separation_of_duties, validate_quality_gates
from .tools.billing import get_billing_costs, forecast_monthly_cost

def main():
    p = argparse.ArgumentParser(description="GCP Landing Zone Multi-Agent CLI Interface")
    subparsers = p.add_subparsers(dest="command")

    # Workflow command
    wf_parser = subparsers.add_parser("workflow", help="Execute workflow with an objective")
    wf_parser.add_argument("objective", nargs="?", default="Create a GCP Landing Zone application environment using Terraform with security, FinOps, testing and operational controls.")

    # Billing command
    subparsers.add_parser("billing", help="Inspect GCP billing costs and forecasts")

    # Governance command
    gov_parser = subparsers.add_parser("governance", help="Check governance policies (SoD and Quality Gates)")
    gov_parser.add_argument("--author", default="agent_01")
    gov_parser.add_argument("--reviewer", default="agent_02")
    gov_parser.add_argument("--action", default="iam_policy_change")

    args = p.parse_args()

    if args.command == "billing":
        costs = get_billing_costs()
        forecast = forecast_monthly_cost(costs["total_cost_usd"])
        print("\n=== GCP BILLING & COST MONITORING REPORT ===")
        print(json.dumps({"costs": costs, "forecast": forecast}, indent=2))
    elif args.command == "governance":
        sod = validate_separation_of_duties(args.author, args.reviewer, args.action)
        qgate = validate_quality_gates("security", {"critical_vulnerabilities": 0})
        print("\n=== GOVERNANCE POLICY EVALUATION ===")
        print(json.dumps({"sod_check": sod, "quality_gate": qgate}, indent=2))
    else:
        obj = getattr(args, "objective", "Create a GCP Landing Zone application environment using Terraform with security, FinOps, testing and operational controls.")
        result = run(obj)
        print("\n=== ENGINEERING ORCHESTRATOR ===\n")
        print(result.get("final_response", "No response returned."))

if __name__ == "__main__":
    main()
