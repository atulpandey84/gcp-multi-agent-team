import os
import re

root = 'c:/Users/atulk/OneDrive/Development/gcp-multi-agent-team'
files_to_fix = [
    'src/multi_agent_team/memory/manager.py',
    'src/multi_agent_team/orchestration/state_machine.py',
    'src/multi_agent_team/api/main.py',
]

for rel_path in files_to_fix:
    path = os.path.join(root, rel_path)
    with open(path, 'r') as f:
        content = f.read()
    
    # Replace all 'from src.multi_agent_team' with 'from multi_agent_team'
    new_content = content.replace('from src.multi_agent_team', 'from multi_agent_team')
    
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f'Fixed: {rel_path}')
    else:
        print(f'No changes needed: {rel_path}')

print('Done fixing imports')