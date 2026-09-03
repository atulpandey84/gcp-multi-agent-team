"""
Tool Registration

Centralized registration of all specialized tools for the multi-agent system.
"""

from .base import ToolRegistry, get_tool_registry

# Import all tool classes
from .architecture import (
    ResourceDesignValidationTool,
    NetworkDesignValidationTool,
    IAMModelDesignTool,
    ThreatModelingTool,
)
from .development import (
    CodeQualityAnalysisTool,
    APIContractValidationTool,
    DependencyCheckTool,
    SecurityChecklistTool,
)
from .devops import (
    TerraformValidationTool,
    CloudBuildPipelineTool,
    MonitoringAlertConfigurationTool,
    CostAnalysisTool,
)
from .testing import (
    TestExecutionOrchestrationTool,
    CoverageAnalysisTool,
    PerformanceTestingTool,
    DefectManagementTool,
)
from .management import (
    IncidentManagementTool,
    OperationalReadinessTool,
    SLOTrackingAndReportingTool,
    RunbookExecutionTool,
)


def register_all_tools() -> ToolRegistry:
    """
    Register all specialized tools with the global registry.
    
    Returns:
        ToolRegistry: The populated tool registry
    """
    registry = get_tool_registry()
    
    # Architecture Tools
    registry.register(ResourceDesignValidationTool("architecture.resource_design_validation", ["platform_architect", "solution_architect"]))
    registry.register(NetworkDesignValidationTool("architecture.network_design_validation", ["platform_architect", "cloud_infrastructure_engineer"]))
    registry.register(IAMModelDesignTool("architecture.iam_design", ["security_architect", "platform_architect"]))
    registry.register(ThreatModelingTool("architecture.threat_modeling", ["security_architect"]))
    
    # Development Tools
    registry.register(CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer", "frontend_engineer", "development_lead"]))
    registry.register(APIContractValidationTool("development.api_contract_validation", ["backend_engineer", "integration_engineer", "development_lead"]))
    registry.register(DependencyCheckTool("development.dependency_check", ["backend_engineer", "frontend_engineer", "integration_engineer"]))
    registry.register(SecurityChecklistTool("development.security_checklist", ["backend_engineer", "frontend_engineer", "integration_engineer"]))
    
    # DevOps Tools
    registry.register(TerraformValidationTool("devops.terraform_validation", ["cloud_infrastructure_engineer", "devops_lead"]))
    registry.register(CloudBuildPipelineTool("devops.cloud_build_pipeline", ["cicd_engineer", "devops_lead"]))
    registry.register(MonitoringAlertConfigurationTool("devops.monitoring_alert_config", ["sre_observability_engineer", "devops_lead"]))
    registry.register(CostAnalysisTool("devops.cost_analysis", ["finops_engineer", "devops_lead"]))
    
    # Testing Tools
    registry.register(TestExecutionOrchestrationTool("testing.test_execution_orchestration", ["test_automation_engineer", "qa_lead"]))
    registry.register(CoverageAnalysisTool("testing.coverage_analysis", ["test_automation_engineer", "qa_lead"]))
    registry.register(PerformanceTestingTool("testing.performance_testing", ["nfr_test_engineer", "qa_lead"]))
    registry.register(DefectManagementTool("testing.defect_management", ["qa_lead", "test_automation_engineer"]))
    
    # Management Tools
    registry.register(IncidentManagementTool("management.incident_management", ["application_management_lead", "application_support_engineer", "production_reliability_engineer"]))
    registry.register(OperationalReadinessTool("management.operational_readiness", ["application_management_lead", "production_reliability_engineer"]))
    registry.register(SLOTrackingAndReportingTool("management.slo_tracking", ["production_reliability_engineer", "application_management_lead"]))
    registry.register(RunbookExecutionTool("management.runbook_execution", ["application_support_engineer", "production_reliability_engineer"]))
    
    return registry


# Initialize on import
__all__ = [
    "register_all_tools",
    "get_tool_registry",
    # Architecture tools
    "ResourceDesignValidationTool",
    "NetworkDesignValidationTool",
    "IAMModelDesignTool",
    "ThreatModelingTool",
    # Development tools
    "CodeQualityAnalysisTool",
    "APIContractValidationTool",
    "DependencyCheckTool",
    "SecurityChecklistTool",
    # DevOps tools
    "TerraformValidationTool",
    "CloudBuildPipelineTool",
    "MonitoringAlertConfigurationTool",
    "CostAnalysisTool",
    # Testing tools
    "TestExecutionOrchestrationTool",
    "CoverageAnalysisTool",
    "PerformanceTestingTool",
    "DefectManagementTool",
    # Management tools
    "IncidentManagementTool",
    "OperationalReadinessTool",
    "SLOTrackingAndReportingTool",
    "RunbookExecutionTool",
]
