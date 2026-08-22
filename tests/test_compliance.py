import os
import yaml


def test_agent_artifacts_exist():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    contracts_path = os.path.join(repo_root, 'config', 'agents_contracts.yaml')
    assert os.path.exists(contracts_path), 'contracts file missing'
    with open(contracts_path, 'r') as f:
        contracts = yaml.safe_load(f)
    assert isinstance(contracts, dict)
    agents = contracts.get('agents', [])
    for entry in agents:
        aid = entry.get('id')
        assert aid, 'agent id missing in contract entry'
        art_dir = os.path.join(repo_root, 'config', 'agents_artifacts', aid)
        assert os.path.isdir(art_dir), f'artifacts folder missing for {aid}'
        prompt = os.path.join(art_dir, 'prompt.txt')
        io_schema = os.path.join(art_dir, 'io_schema.yaml')
        assert os.path.exists(prompt), f'prompt.txt missing for {aid}'
        assert os.path.exists(io_schema), f'io_schema.yaml missing for {aid}'
        # at least one ADR file
        found_adr = False
        for n in os.listdir(art_dir):
            if n.startswith('ADR') and n.endswith('.md'):
                found_adr = True
                break
        assert found_adr, f'ADR file missing for {aid}'
