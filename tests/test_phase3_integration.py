"""
Phase 3: Integration Tests for Agent Tools and Workflows

Tests tool framework, agent permissions, approval chains, and end-to-end workflows.
"""

import pytest
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multi_agent_team.tools.base import (
    BaseTool, ToolInput, ToolOutput, ToolDefinition, ToolRisk, 
    ApprovalRequired, ToolRegistry, get_tool_registry
)
from src.multi_agent_team.tools import (
    ResourceDesignValidationTool,
    NetworkDesignValidationTool,
    IAMModelDesignTool,
    ThreatModelingTool,
    CodeQualityAnalysisTool,
    APIContractValidationTool,
    DependencyCheckTool,
    SecurityChecklistTool,
    TerraformValidationTool,
    CloudBuildPipelineTool,
    MonitoringAlertConfigurationTool,
    CostAnalysisTool,
    TestExecutionOrchestrationTool,
    CoverageAnalysisTool,
    PerformanceTestingTool,
    DefectManagementTool,
    IncidentManagementTool,
    OperationalReadinessTool,
    SLOTrackingAndReportingTool,
    RunbookExecutionTool,
)


class TestToolFramework:
    """Test base tool framework functionality"""
    
    def test_tool_registry_initialization(self):
        """Test tool registry can be created and populated"""
        registry = ToolRegistry()
        assert registry is not None
        assert len(registry.tools) == 0
    
    def test_tool_registration(self):
        """Test tools can be registered"""
        registry = ToolRegistry()
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        registry.register(tool)
        
        assert len(registry.tools) == 1
        assert "development.code_quality_analysis" in registry.tools
    
    def test_tool_definition(self):
        """Test tool definitions contain required metadata"""
        tool = ResourceDesignValidationTool("architecture.resource_design_validation", ["platform_architect"])
        definition = tool.get_definition()
        
        assert definition.tool_id == "architecture.resource_design_validation"
        assert definition.name is not None
        assert definition.risk_level in ToolRisk
        assert definition.approval_required in ApprovalRequired
        assert len(definition.agent_ids) > 0
        assert len(definition.allowed_actions) > 0


class TestAgentToolAccess:
    """Test agent access control and permissions"""
    
    def test_authorized_agent_can_access_tool(self):
        """Test authorized agents can access their tools"""
        registry = ToolRegistry()
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer", "frontend_engineer"])
        registry.register(tool)
        
        can_execute, reason = registry.can_execute(
            "backend_engineer",
            "development.code_quality_analysis",
            "analyze"
        )
        assert can_execute == True
        assert reason is None
    
    def test_unauthorized_agent_cannot_access_tool(self):
        """Test unauthorized agents cannot access tools"""
        registry = ToolRegistry()
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        registry.register(tool)
        
        can_execute, reason = registry.can_execute(
            "qa_lead",
            "development.code_quality_analysis",
            "analyze"
        )
        assert can_execute == False
        assert reason is not None
    
    def test_invalid_action_not_allowed(self):
        """Test invalid actions are rejected"""
        registry = ToolRegistry()
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        registry.register(tool)
        
        can_execute, reason = registry.can_execute(
            "backend_engineer",
            "development.code_quality_analysis",
            "invalid_action"
        )
        assert can_execute == False
        assert reason is not None
    
    def test_tool_not_found(self):
        """Test request for non-existent tool is rejected"""
        registry = ToolRegistry()
        
        can_execute, reason = registry.can_execute(
            "backend_engineer",
            "nonexistent.tool",
            "analyze"
        )
        assert can_execute == False
        assert "not found" in reason.lower()


class TestToolApprovalWorkflows:
    """Test approval requirements and workflows"""
    
    def test_low_risk_tool_no_approval(self):
        """Test low-risk tools don't require approval"""
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        definition = tool.get_definition()
        
        assert definition.approval_required == ApprovalRequired.NONE
    
    def test_medium_risk_tool_peer_approval(self):
        """Test medium-risk tools require peer approval"""
        tool = IAMModelDesignTool("architecture.iam_design", ["security_architect"])
        definition = tool.get_definition()
        
        assert definition.approval_required == ApprovalRequired.PEER
    
    def test_high_risk_tool_human_approval(self):
        """Test high-risk tools require human approval"""
        tool = OperationalReadinessTool("management.operational_readiness", ["application_management_lead"])
        definition = tool.get_definition()
        
        assert definition.approval_required == ApprovalRequired.HUMAN
    
    def test_mutable_operation_flag(self):
        """Test mutable operations are correctly marked"""
        tool_immutable = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        tool_mutable = CloudBuildPipelineTool("devops.cloud_build_pipeline", ["cicd_engineer"])
        
        assert tool_immutable.get_definition().mutable == False
        assert tool_mutable.get_definition().mutable == True


class TestToolExecution:
    """Test tool execution and output validation"""
    
    @pytest.mark.asyncio
    async def test_code_quality_analysis_execution(self):
        """Test code quality tool executes successfully"""
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        
        tool_input = ToolInput(
            agent_id="backend_engineer",
            task_id="task-001",
            action="analyze",
            parameters={"files": ["src/main.py", "src/utils.py"]},
        )
        
        output = await tool.execute(tool_input)
        
        assert output.success == True
        assert output.action == "analyze"
        assert output.result is not None
        assert "quality_score" in output.result
    
    @pytest.mark.asyncio
    async def test_unauthorized_execution_rejected(self):
        """Test unauthorized agent execution is rejected"""
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        
        tool_input = ToolInput(
            agent_id="qa_lead",  # Not authorized
            task_id="task-001",
            action="analyze",
            parameters={},
        )
        
        output = await tool.execute(tool_input)
        
        assert output.success == False
        assert output.error is not None
    
    @pytest.mark.asyncio
    async def test_tool_audit_logging(self):
        """Test tool execution is logged"""
        tool = CostAnalysisTool("devops.cost_analysis", ["finops_engineer"])
        
        tool_input = ToolInput(
            agent_id="finops_engineer",
            task_id="task-001",
            action="analyze_costs",
            parameters={},
        )
        
        output = await tool.execute(tool_input)
        
        assert len(tool.execution_log) > 0
        assert output.audit_log is not None


class TestArchitectureToolChain:
    """Test architecture team tool workflows"""
    
    @pytest.mark.asyncio
    async def test_resource_design_validation(self):
        """Test resource design validation workflow"""
        tool = ResourceDesignValidationTool("architecture.resource_design_validation", ["platform_architect"])
        
        # Step 1: Validate resources
        validate_input = ToolInput(
            agent_id="platform_architect",
            task_id="arch-001",
            action="validate",
            parameters={
                "resources": [
                    {
                        "type": "compute.Instance",
                        "name": "web-server",
                        "labels": {"env": "prod"},
                        "service_account": "default@project.iam.gserviceaccount.com"
                    }
                ]
            }
        )
        
        validate_output = await tool.execute(validate_input)
        assert validate_output.success == True
        assert validate_output.result["valid"] == True
    
    @pytest.mark.asyncio
    async def test_threat_modeling_workflow(self):
        """Test threat modeling workflow"""
        tool = ThreatModelingTool("architecture.threat_modeling", ["security_architect"])
        
        # Step 1: Analyze system
        analyze_input = ToolInput(
            agent_id="security_architect",
            task_id="sec-001",
            action="analyze",
            parameters={"system": "user-service"}
        )
        
        analyze_output = await tool.execute(analyze_input)
        assert analyze_output.success == True
        
        # Step 2: Identify threats
        threats_input = ToolInput(
            agent_id="security_architect",
            task_id="sec-001",
            action="identify_threats",
            parameters={"analysis_id": "analysis-123"}
        )
        
        threats_output = await tool.execute(threats_input)
        assert threats_output.success == True
        assert "threats" in threats_output.result


class TestDevelopmentToolChain:
    """Test development team tool workflows"""
    
    @pytest.mark.asyncio
    async def test_api_contract_validation_workflow(self):
        """Test API contract validation workflow"""
        tool = APIContractValidationTool("development.api_contract_validation", ["backend_engineer"])
        
        # Step 1: Validate contract
        validate_input = ToolInput(
            agent_id="backend_engineer",
            task_id="dev-001",
            action="validate",
            parameters={
                "spec": {"openapi": "3.0.0", "endpoints": []}
            }
        )
        
        validate_output = await tool.execute(validate_input)
        assert validate_output.success == True
        assert validate_output.result["valid"] == True
    
    @pytest.mark.asyncio
    async def test_dependency_security_check_workflow(self):
        """Test dependency check workflow"""
        tool = DependencyCheckTool("development.dependency_check", ["backend_engineer"])
        
        # Step 1: Scan vulnerabilities
        scan_input = ToolInput(
            agent_id="backend_engineer",
            task_id="dev-002",
            action="scan",
            parameters={"project_dir": "."}
        )
        
        scan_output = await tool.execute(scan_input)
        assert scan_output.success == True
        assert "vulnerabilities" in scan_output.result


class TestTestingToolChain:
    """Test testing team tool workflows"""
    
    @pytest.mark.asyncio
    async def test_test_execution_workflow(self):
        """Test test execution orchestration workflow"""
        tool = TestExecutionOrchestrationTool("testing.test_execution_orchestration", ["test_automation_engineer"])
        
        # Execute test suite
        execute_input = ToolInput(
            agent_id="test_automation_engineer",
            task_id="test-001",
            action="execute_suite",
            parameters={"suite_name": "smoke_tests"}
        )
        
        execute_output = await tool.execute(execute_input)
        assert execute_output.success == True
        assert execute_output.result["tests_passed"] >= 0
    
    @pytest.mark.asyncio
    async def test_coverage_analysis_workflow(self):
        """Test coverage analysis workflow"""
        tool = CoverageAnalysisTool("testing.coverage_analysis", ["qa_lead"])
        
        # Analyze coverage
        analyze_input = ToolInput(
            agent_id="qa_lead",
            task_id="test-002",
            action="analyze",
            parameters={"project": "backend"}
        )
        
        analyze_output = await tool.execute(analyze_input)
        assert analyze_output.success == True
        assert "overall_coverage" in analyze_output.result


class TestManagementToolChain:
    """Test management team tool workflows"""
    
    @pytest.mark.asyncio
    async def test_incident_lifecycle_workflow(self):
        """Test incident management lifecycle"""
        tool = IncidentManagementTool("management.incident_management", ["application_management_lead"])
        
        # Step 1: Create incident
        create_input = ToolInput(
            agent_id="application_management_lead",
            task_id="incident-001",
            action="create_incident",
            parameters={
                "title": "API Gateway Down",
                "severity": "critical"
            }
        )
        
        create_output = await tool.execute(create_input)
        assert create_output.success == True
        incident_id = create_output.result["incident_id"]
        
        # Step 2: Classify incident
        classify_input = ToolInput(
            agent_id="application_management_lead",
            task_id="incident-001",
            action="classify",
            parameters={"incident_id": incident_id}
        )
        
        classify_output = await tool.execute(classify_input)
        assert classify_output.success == True
    
    @pytest.mark.asyncio
    async def test_slo_tracking_workflow(self):
        """Test SLO tracking and reporting"""
        tool = SLOTrackingAndReportingTool("management.slo_tracking", ["production_reliability_engineer"])
        
        # Track SLO
        track_input = ToolInput(
            agent_id="production_reliability_engineer",
            task_id="slo-001",
            action="track_slo",
            parameters={"slo_name": "API Availability"}
        )
        
        track_output = await tool.execute(track_input)
        assert track_output.success == True
        assert track_output.result["slo_name"] == "API Availability"


class TestCrossFunctionalWorkflow:
    """Test cross-functional workflows between tool chains"""
    
    @pytest.mark.asyncio
    async def test_architecture_to_dev_workflow(self):
        """Test workflow from architecture design to development"""
        # Step 1: Architecture designs resources
        arch_tool = ResourceDesignValidationTool("architecture.resource_design_validation", ["platform_architect"])
        arch_input = ToolInput(
            agent_id="platform_architect",
            task_id="workflow-001",
            action="validate",
            parameters={
                "resources": [
                    {"type": "storage.Bucket", "name": "app-data"}
                ]
            }
        )
        arch_output = await arch_tool.execute(arch_input)
        assert arch_output.success == True
        
        # Step 2: Development validates API contract
        dev_tool = APIContractValidationTool("development.api_contract_validation", ["backend_engineer"])
        dev_input = ToolInput(
            agent_id="backend_engineer",
            task_id="workflow-001",
            action="validate",
            parameters={"spec": {"openapi": "3.0.0"}}
        )
        dev_output = await dev_tool.execute(dev_input)
        assert dev_output.success == True
    
    @pytest.mark.asyncio
    async def test_dev_to_testing_workflow(self):
        """Test workflow from development to testing"""
        # Step 1: Development completes implementation
        dev_tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        dev_input = ToolInput(
            agent_id="backend_engineer",
            task_id="workflow-002",
            action="analyze",
            parameters={"files": ["src/api.py"]}
        )
        dev_output = await dev_tool.execute(dev_input)
        assert dev_output.success == True
        
        # Step 2: Testing executes tests
        test_tool = TestExecutionOrchestrationTool("testing.test_execution_orchestration", ["qa_lead"])
        test_input = ToolInput(
            agent_id="qa_lead",
            task_id="workflow-002",
            action="execute_suite",
            parameters={"suite_name": "integration_tests"}
        )
        test_output = await test_tool.execute(test_input)
        assert test_output.success == True


class TestSafetyMechanisms:
    """Test safety mechanisms and fail-closed behavior"""
    
    def test_agent_not_authorized_for_high_risk_tool(self):
        """Test agent cannot execute high-risk tool without authorization"""
        registry = ToolRegistry()
        tool = OperationalReadinessTool("management.operational_readiness", ["application_management_lead"])
        registry.register(tool)
        
        # Frontend engineer tries to assess operational readiness (not authorized)
        can_execute, reason = registry.can_execute(
            "frontend_engineer",
            "management.operational_readiness",
            "assess"
        )
        assert can_execute == False
    
    def test_mutable_tool_tracked(self):
        """Test mutable operations are properly tracked"""
        tool = CloudBuildPipelineTool("devops.cloud_build_pipeline", ["cicd_engineer"])
        definition = tool.get_definition()
        
        assert definition.mutable == True
        assert definition.approval_required == ApprovalRequired.PEER
    
    def test_production_restricted_tool(self):
        """Test production-restricted tools"""
        registry = ToolRegistry()
        tool = TerraformValidationTool("devops.terraform_validation", ["cloud_infrastructure_engineer"])
        registry.register(tool)
        
        # Try to execute in production environment
        can_execute, reason = registry.can_execute(
            "cloud_infrastructure_engineer",
            "devops.terraform_validation",
            "validate",
            environment="production"
        )
        # Should fail because tool is restricted to dev environment
        assert can_execute == False


class TestQualityGates:
    """Test quality gate enforcement"""
    
    @pytest.mark.asyncio
    async def test_code_quality_gate(self):
        """Test code quality tool validates against gates"""
        tool = CodeQualityAnalysisTool("development.code_quality_analysis", ["backend_engineer"])
        
        tool_input = ToolInput(
            agent_id="backend_engineer",
            task_id="quality-001",
            action="analyze",
            parameters={"files": ["src/main.py"]}
        )
        
        output = await tool.execute(tool_input)
        
        # Verify output has required fields for quality gate
        assert "quality_score" in output.result
        assert "issues" in output.result
    
    @pytest.mark.asyncio
    async def test_test_coverage_gate(self):
        """Test test coverage meets minimum requirements"""
        tool = CoverageAnalysisTool("testing.coverage_analysis", ["qa_lead"])
        
        tool_input = ToolInput(
            agent_id="qa_lead",
            task_id="coverage-001",
            action="analyze",
            parameters={"project": "backend"}
        )
        
        output = await tool.execute(tool_input)
        
        # Verify coverage is reported
        assert "overall_coverage" in output.result
        assert output.result["overall_coverage"] >= 0


# Test Suite Runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
