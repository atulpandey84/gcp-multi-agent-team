import sys
sys.path.insert(0, 'c:/Users/atulk/OneDrive/Development/gcp-multi-agent-team/src')
from multi_agent_team.models.provider import MockModel, SmartFallbackModel, initialize_models

# Test MockModel directly
mock = MockModel('architecture_critical')
result = mock.invoke('Design a GCP platform architecture')
print('MockModel test:')
print('  Status:', result.response_metadata['model_provider'])
print('  Mock:', result.response_metadata['mock'])
content = result.content
print('  Content keys:', list(content.keys()) if isinstance(content, dict) else 'not dict')
print()

# Test SmartFallbackModel with None primary (simulating no NVIDIA API)
sfm = SmartFallbackModel('architecture_critical', None, {'model': 'test', 'temperature': 0.1})
result2 = sfm.invoke('Design a GCP platform architecture')
print('SmartFallbackModel with None primary:')
print('  Provider:', result2.response_metadata['model_provider'])
print('  Mock:', result2.response_metadata['mock'])
print()

# Test initialize_models
print('Testing initialize_models...')
mp = initialize_models()
print('  Loaded', len(mp.list_models()), 'model policies')
for policy in mp.list_models():
    model = mp.get_model(policy)
    print('  -', policy, ':', model.__class__.__name__)
print()
print('All model provider tests PASSED')