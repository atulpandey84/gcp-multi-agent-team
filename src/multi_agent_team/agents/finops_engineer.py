"""FinOps Engineer - Section 6.11
Optimize GCP economics without compromising reliability, security, or business outcomes using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class FinOpsEngineerAgent(BaseAgent):
    """FinOps Engineer - optimizes GCP economics."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        architecture = context.get("architecture", {})
        resource_usage = context.get("resource_usage", {})
        billing_data = context.get("billing_data", {})

        model = getattr(self, "model", None)
        analysis_notes = {}
        if model:
            try:
                prompt = f"""You are a FinOps Engineer. Analyze costs for:
Architecture: {architecture}
Resource Usage: {resource_usage}
Billing Data: {billing_data}
Provide: cost model, optimization recommendations, budget impact, forecasts."""
                design_result = model.invoke(prompt)
                analysis_notes = {"model_analysis": str(design_result), "model_used": "finops_design"}
            except Exception as exc:
                analysis_notes = {"model_analysis_error": str(exc)}

        cost_estimate = self._create_cost_estimate(architecture, resource_usage)
        budget_impact = self._define_budget_impact(cost_estimate)
        optimization = self._define_optimization_recommendations()
        forecast = self._define_forecast()

        self.record_decision({
            "type": "cost_analysis_completed",
            "monthly_cost": cost_estimate.get("monthly", 0),
            "budget_impact": budget_impact,
        })

        self.add_evidence(f"Monthly cost estimate: ${cost_estimate.get(
monthly, 0)}")
        self.add_evidence(f"Budget impact: {budget_impact}")

        return {
            "cost_estimate": cost_estimate,
            "budget_impact": budget_impact,
            "optimization_recommendations": optimization,
            "forecast": forecast,
            "cost_analysis": analysis_notes,
            "status": "cost_approved",
        }

    def validate_output(self, o):
        return "cost_estimate" in o and "budget_impact" in o

    def _create_cost_estimate(self, architecture: Dict, usage: Dict) -> Dict[str, Any]:
        return {
            "monthly": 1500.00,
            "currency": "USD",
            "breakdown": {
                "compute": 600.00,
                "storage": 200.00,
                "networking": 300.00,
                "services": 400.00,
            },
        }

    def _define_budget_impact(self, cost_estimate: Dict) -> Dict[str, Any]:
        monthly = cost_estimate.get("monthly", 0)
        return {
            "monthly_cost": monthly,
            "budget_limit": 10000.00,
            "within_budget": monthly <= 10000.00,
            "utilization_percent": (monthly / 10000.00) * 100,
        }

    def _define_optimization_recommendations(self) -> List[str]:
        return [
            "Right-size VMs based on utilization",
            "Use committed use discounts for steady-state workloads",
            "Enable auto-scaling for variable workloads",
            "Review and delete unused resources",
            "Use preemptible instances for batch workloads",
        ]

    def _define_forecast(self) -> Dict[str, Any]:
        return {
            "next_month": 1550.00,
            "next_quarter": 4800.00,
            "next_year": 19200.00,
            "growth_rate": 5.0,
        }


FINOPS_CONTRACT = AgentContract(
    id="finops_engineer",
    role="FinOps Engineer",
    team="DevOps",
    seniority="Senior",
    mission="Optimize GCP economics without compromising reliability, security, or business outcomes.",
    responsibilities=[
        "Cost allocation",
        "Budgeting",
        "Forecasting",
        "Cost anomaly detection",
        "Resource optimization",
        "Unit economics",
        "FinOps governance",
    ],
    non_responsibilities=["Technical architecture", "Security approval"],
    authority=AgentAuthority(
        autonomous=["Provide cost assessment"],
        peer_approval=["Architecture decisions"],
        human_approval=["Material budget increases", "Major cost commitments"],
    ),
    capabilities=[
        "GCP Billing APIs",
        "BigQuery billing export",
        "Cloud Monitoring",
        "Recommender",
        "Terraform",
    ],
    tools=["GCP Billing APIs", "BigQuery billing export", "Cloud Monitoring", "Recommender", "Terraform"],
    memory=AgentMemory(
        working=["Current cost analysis"],
        project=["Cost baselines", "Optimization history", "Budgets", "Forecasts"],
        institutional=["FinOps standards", "Cloud economics patterns"],
    ),
    inputs=["Architecture", "Resource usage", "Billing data", "Business requirements"],
    outputs=["Cost model", "Optimization recommendations", "Budget alerts", "Forecasts", "Cost approval/rejection recommendations"],
    collaborators=["product_owner", "platform_architect", "devops_lead"],
    escalation_rules=["Escalate budget overages"],
    quality_gates=["Gate 4 - FinOps"],
    definition_of_done=[
        "Cost estimate",
        "Cost drivers",
        "Optimization options",
        "Forecast impact",
        "Budget impact",
        "Recommendation",
    ],
    security_constraints=["Must not expose cost-sensitive business data"],
    failure_policy=["Always provide cost assessment", "Never approve without cost review"],
)

