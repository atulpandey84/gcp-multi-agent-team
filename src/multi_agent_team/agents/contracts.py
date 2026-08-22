from pathlib import Path
import yaml
from typing import Dict, Any


CONTRACTS_PATH = Path(__file__).resolve().parents[3] / "config" / "agents_contracts.yaml"


def load_contracts() -> Dict[str, Dict[str, Any]]:
    if not CONTRACTS_PATH.exists():
        raise FileNotFoundError(f"Contracts file not found: {CONTRACTS_PATH}")
    with open(CONTRACTS_PATH, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    agents = data.get("agents", [])
    mapping: Dict[str, Dict[str, Any]] = {}
    for contract in agents:
        if not isinstance(contract, dict):
            raise ValueError("Each agent contract must be a mapping")
        validate_contract(contract)
        agent_id = contract["id"]
        if agent_id in mapping:
            raise ValueError(f"Duplicate agent contract: {agent_id}")
        mapping[agent_id] = contract
    return mapping


def get_agent_contract(agent_id: str) -> Dict[str, Any] | None:
    return load_contracts().get(agent_id)


def validate_contract(contract: Dict[str, Any]) -> bool:
    required = [
        "id", "role", "team", "mission", "seniority", "responsibilities",
        "non_responsibilities", "authority", "capabilities", "tools", "memory",
        "inputs", "outputs", "collaborators", "escalation_rules", "quality_gates",
        "definition_of_done", "security_constraints", "failure_policy",
    ]
    missing = [k for k in required if k not in contract]
    if missing:
        raise ValueError(f"Agent contract missing required keys: {missing}")
    # basic authority shape
    auth = contract.get("authority")
    if not isinstance(auth, dict):
        raise ValueError("authority must be a mapping")
    for key in ("autonomous", "peer_approval", "human_approval"):
        if not isinstance(auth.get(key), list):
            raise ValueError(f"authority.{key} must be a list")
    if not isinstance(contract.get("memory"), dict):
        raise ValueError("memory must be a mapping")
    for key in ("working", "project", "institutional"):
        if not isinstance(contract["memory"].get(key), list):
            raise ValueError(f"memory.{key} must be a list")
    return True


if __name__ == "__main__":
    agents = load_contracts()
    for aid, contract in agents.items():
        validate_contract(contract)
    print(f"Loaded {len(agents)} agent contracts from {CONTRACTS_PATH}")
