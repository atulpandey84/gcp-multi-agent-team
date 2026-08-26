from multi_agent_team.tools.billing import get_billing_costs, forecast_monthly_cost
from multi_agent_team.main import main
import sys

def test_billing_tool_costs_and_forecast():
    costs = get_billing_costs("prj-test-01")
    assert costs["status"] == "success"
    assert costs["project_id"] == "prj-test-01"
    assert costs["total_cost_usd"] > 0
    assert len(costs["service_breakdown"]) > 0

    forecast = forecast_monthly_cost(costs["total_cost_usd"], days_elapsed=15, days_in_month=30)
    assert forecast["days_elapsed"] == 15
    assert forecast["projected_monthly_cost_usd"] == round(costs["total_cost_usd"] * 2, 2)

def test_cli_billing_command(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "billing"])
    main()
    captured = capsys.readouterr()
    assert "GCP BILLING & COST MONITORING REPORT" in captured.out

def test_cli_governance_command(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "governance", "--author", "agent_a", "--reviewer", "agent_b"])
    main()
    captured = capsys.readouterr()
    assert "GOVERNANCE POLICY EVALUATION" in captured.out
    assert "Separation of Duties check passed" in captured.out
