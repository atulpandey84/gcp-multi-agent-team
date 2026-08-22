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
    mapping = {a.get("id"): a for a in agents}
    return mapping


def get_agent_contract(agent_id: str) -> Dict[str, Any] | None:
    return load_contracts().get(agent_id)


def validate_contract(contract: Dict[str, Any]) -> bool:
    required = ["id", "role", "team", "mission", "seniority", "responsibilities", "authority"]
    missing = [k for k in required if k not in contract]
    if missing:
        raise ValueError(f"Agent contract missing required keys: {missing}")
    # basic authority shape
    auth = contract.get("authority")
    if not isinstance(auth, dict):
        raise ValueError("authority must be a mapping")
    return True


if __name__ == "__main__":
    agents = load_contracts()
    for aid, contract in agents.items():
        validate_contract(contract)
    print(f"Loaded {len(agents)} agent contracts from {CONTRACTS_PATH}")
