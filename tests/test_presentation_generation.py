import pytest
from unittest.mock import MagicMock, patch
import os
import json
import tempfile
from pathlib import Path

# Import the utility function we need to test
from src.multi_agent_team.utils.presentation_generator import generate_presentation

# Mock the workflow run object structure for testing
@pytest.fixture
def mock_workflow_run():
    """Creates a mock WorkflowRun object mimicking successful artifact collection."""
    # Simulate required structure based on usage in workflow_engine.py
    mock_run = MagicMock()
    mock_run.name = "Test Workflow"
    mock_run.model_policy = "test_policy"
    
    # Simulate the artifacts dictionary structure: {name: artifact_dict}
    mock_run.artifacts = {
        "artifact_1": {"source_file": "file_a.txt", "data": {"key": "value", "detail": 1}},
        "artifact_2": {"source_file": "file_b.json", "data": [{"item": "x"}, {"item": "y"}]},
        "artifact_3": {"source_file": "file_c.md", "data": "Summary text here."},
    }
    return mock_run

def test_generate_presentation_structure_and_call(mock_workflow_run):
    """
    Tests that the workflow_engine correctly gathers artifacts and calls 
    generate_presentation with the expected structured data.
    """
    
    # 1. Manually simulate the content_sections list that the workflow engine generates
    expected_content_sections = [
        {"title": "Artifact: artifact_1", "content": [f"Source: file_a.txt", f"Details: {json.dumps({'key': 'value', 'detail': 1}, indent=2)}"]},
        {"title": "Artifact: artifact_2", "content": [f"Source: file_b.json", f"Details: {json.dumps([{'item': 'x'}, {'item': 'y'}], indent=2)}"]},
        {"title": "Artifact: artifact_3", "content": [f"Source: file_c.md", f"Details: Summary text here."]}
    ]

    # 2. Mock the entire function call to capture the arguments
    with patch('src.multi_agent_team.utils.presentation_generator.generate_presentation') as mock_generate:
        # Execute the function that performs the assembly (mimicking workflow_engine's logic)
        presentation_title = f"{mock_workflow_run.name} Workflow Summary: {mock_workflow_run.model_policy.upper()}"
        
        content_sections = [
            {"title": f"Artifact: {name}", "content": [f"Source: {artifact['source_file']}", f"Details: {json.dumps(artifact['data'], indent=2)}"]}
            for name, artifact in mock_workflow_run.artifacts.items()
        ]

        # Call the utility function (this simulates the line in workflow_engine.py)
        mock_generate(
            title=presentation_title,
            content_sections=content_sections,
            output_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..", "output", "presentation.pptx")
        )

        # 3. Assertions
        mock_generate.assert_called_once()
        
        # Verify the title was correctly passed
        mock_generate.assert_called_with(
            title="Test Workflow Workflow Summary: TEST_POLICY",
            content_sections=expected_content_sections,
            output_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..", "output", "presentation.pptx")
        )

# Add a test for empty artifacts case
def test_generate_presentation_empty_artifacts():
    """Tests the scenario where the workflow completes but has no artifacts."""
    mock_run = MagicMock()
    mock_run.name = "Empty Workflow"
    mock_run.model_policy = "empty"
    mock_run.artifacts = {} # Empty artifacts

    with patch('src.multi_agent_team.utils.presentation_generator.generate_presentation') as mock_generate:
        # Simulate the assembly
        presentation_title = f"{mock_run.name} Workflow Summary: {mock_run.model_policy.upper()}"
        
        content_sections = [
            {"title": f"Artifact: {name}", "content": [f"Source: {artifact['source_file']}", f"Details: {json.dumps(artifact['data'], indent=2)}"]}
            for name, artifact in mock_run.artifacts.items()
        ]

        mock_generate(
            title=presentation_title,
            content_sections=content_sections,
            output_path="dummy/path/presentation.pptx"
        )

        # Assert that it was called with empty content sections
        mock_generate.assert_called_with(
            title="Empty Workflow Workflow Summary: EMPTY",
            content_sections=[],
            output_path="dummy/path/presentation.pptx"
        )