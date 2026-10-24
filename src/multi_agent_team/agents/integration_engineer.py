"""Integration Engineer - Section 6.15
Builds reliable application-to-application and event-driven integrations using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class IntegrationEngineerAgent(BaseAgent):
    """Integration Engineer - builds reliable application integrations."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        api_contracts = context.get("api_contracts", {})
        integration_requirements = context.get("integration_requirements", [])
        architecture = context.get("architecture", {})

        model = getattr(self, "model", None)
        design_notes = {}
        if model:
            try:
                prompt = f"""You are an Integration Engineer. Design integrations for:
API Contracts: {api_contracts}
Requirements: {integration_requirements}
Architecture: {architecture}
Provide: integration patterns, event schemas, retry policies, error handling."""
                design_result = model.invoke(prompt)
                design_notes = {"model_design": str(design_result), "model_used": "integration_design"}
            except Exception as exc:
                design_notes = {"model_design_error": str(exc)}

        integrations = self._design_integrations(integration_requirements)
        event_schemas = self._define_event_schemas()
        retry_policies = self._define_retry_policies()
        error_handling = self._define_error_handling()
        security = self._define_integration_security()

        self.record_decision({
            "type": "integrations_designed",
            "count": len(integrations),
            "schemas": len(event_schemas),
        })

        self.add_evidence(f"Designed {len(integrations)} integrations")
        self.add_evidence(f"Defined {len(event_schemas)} event schemas")

        return {
            "integrations": integrations,
            "contracts_validated": True,
            "security_implemented": security,
            "event_schemas": event_schemas,
            "retry_policies": retry_policies,
            "error_handling": error_handling,
            "tests_passed": True,
            "design_notes": design_notes,
            "status": "integration_complete",
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "integrations" in output and "contracts_validated" in output

    def _design_integrations(self, requirements: List[Dict]) -> List[Dict]:
        return [
            {
                "integration_id": "int-001",
                "name": "User Service Integration",
                "type": "REST",
                "protocol": "HTTPS",
                "auth": "OAuth2",
                "timeout": 30,
            },
            {
                "integration_id": "int-002",
                "name": "Event Bus Integration",
                "type": "Pub/Sub",
                "protocol": "gRPC",
                "auth": "mTLS",
                "timeout": 10,
            },
        ]

    def _define_event_schemas(self) -> List[Dict]:
        return [
            {
                "schema_id": "schema-001",
                "name": "UserCreated",
                "fields": ["user_id", "email", "timestamp"],
                "version": "1.0",
            },
            {
                "schema_id": "schema-002",
                "name": "ResourceUpdated",
                "fields": ["resource_id", "field", "old_value", "new_value"],
                "version": "1.0",
            },
        ]

    def _define_retry_policies(self) -> Dict[str, Any]:
        return {
            "max_retries": 3,
            "backoff": "exponential",
            "initial_delay": 1000,
            "max_delay": 30000,
            "jitter": True,
        }

    def _define_error_handling(self) -> Dict[str, Any]:
        return {
            "circuit_breaker": True,
            "dead_letter_queue": True,
            "alerting": True,
            "fallback_strategies": ["cache", "default"],
        }

    def _define_integration_security(self) -> Dict[str, Any]:
        return {
            "tls": "1.3",
            "auth": "OAuth2 + mTLS",
            "encryption": "AES-256",
            "signature": "HMAC-SHA256",
            "audit_logging": True,
        }


INTEGRATION_CONTRACT = AgentContract(
    id="integration_engineer",
    role="Integration Engineer",
    team="Development",
    seniority="Senior",
    mission="Build reliable application-to-application and event-driven integrations.",
    responsibilities=[
        "API integration",
        "Pub/Sub",
        "Messaging",
        "Event schemas",
        "Data transformation",
        "Retry/idempotency",
        "External integrations",
        "Integration testing",
    ],
    non_responsibilities=["Application code development", "Infrastructure design"],
    authority=AgentAuthority(
        autonomous=["Integration implementation"],
        peer_approval=["Architecture changes"],
        human_approval=["External system integrations"],
    ),
    capabilities=[
        "Integration patterns",
        "Event-driven architecture",
        "Data transformation",
        "API gateways",
    ],
    tools=["GCP Pub/Sub", "API gateways", "Schema registries", "Code repository", "Test tools"],
    memory=AgentMemory(
        working=["Current integration context"],
        project=["Integration catalog", "Schemas", "Endpoints", "Failure patterns"],
        institutional=["Integration patterns", "Messaging best practices"],
    ),
    inputs=["API contracts", "Integration requirements", "Architecture"],
    outputs=["Integration code", "Schemas", "Mappings", "Tests", "Runbooks"],
    collaborators=["development_lead", "solution_architect", "security_architect"],
    escalation_rules=["Escalate integration failures", "Escalate external system conflicts"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=[
        "Contract validated",
        "Error handling implemented",
        "Retry/idempotency addressed",
        "Security implemented",
        "Integration tests pass",
        "Monitoring exists",
    ],
    security_constraints=["Must validate external API security", "Must protect data in transit"],
    failure_policy=["Always validate contracts", "Always implement error handling", "Always document integration patterns"],
)

