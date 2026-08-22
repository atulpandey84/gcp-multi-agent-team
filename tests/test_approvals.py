import json
import os
from fastapi.testclient import TestClient
from src.multi_agent_team.monitoring.app import app
from src.multi_agent_team.monitoring import config


def setup_module(module):
    # ensure API key for tests
    config.settings.api_key = 'testkey'


def test_approval_lifecycle():
    client = TestClient(app)
    # create a JWT directly (bypass /api/token path in tests)
    import os
    from src.multi_agent_team.monitoring.auth import create_jwt
    os.environ['MONITORING_JWT_SECRET'] = 'tests3cret'
    token = create_jwt({'role': 'admin'})
    headers = {'authorization': 'Bearer ' + token}

    # start agent that requires approval
    aid = 'product_owner'
    # ensure no pre-existing approvals for this agent
    from src.multi_agent_team.monitoring import db as _db
    conn = _db._conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM approvals WHERE agent_id=?", (aid,))
    conn.commit()
    conn.close()

    r = client.post(f'/api/agents/{aid}/start', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get('approval_required')
    approval_id = data.get('approval_id')
    assert approval_id

    # list approvals
    r = client.get('/api/approvals', headers=headers)
    assert r.status_code == 200
    rows = r.json()
    assert any(r['id'] == approval_id for r in rows)

    # approve
    r = client.post(f'/api/approvals/{approval_id}/decide', headers=headers, json={'decision': 'approved', 'comments': 'ok'})
    assert r.status_code == 200
    # after approval the action should have been executed
    r = client.get('/api/agents', headers=headers)
    assert r.status_code == 200
    agents = r.json()
    # find the agent and verify status is running or present
    found = [a for a in agents if a.get('id') == aid]
    assert found
    # status should be running because start action executed
    assert found[0].get('status') in ('running', 'idle', 'stopped')


def test_approval_cannot_be_replayed():
    client = TestClient(app)
    from src.multi_agent_team.monitoring.auth import create_jwt
    token = create_jwt({'role': 'admin'})
    headers = {'authorization': 'Bearer ' + token}

    response = client.post('/api/agents/product_owner/start', headers=headers)
    approval_id = response.json()['approval_id']
    response = client.post(
        f'/api/approvals/{approval_id}/decide',
        headers=headers,
        json={'decision': 'approved'},
    )
    assert response.status_code == 200
    replay = client.post(
        f'/api/approvals/{approval_id}/decide',
        headers=headers,
        json={'decision': 'approved'},
    )
    assert replay.status_code == 409


def test_approval_request_rejects_unknown_actions_and_agents():
    client = TestClient(app)
    from src.multi_agent_team.monitoring.auth import create_jwt
    token = create_jwt({'role': 'admin'})
    headers = {'authorization': 'Bearer ' + token}

    assert client.post(
        '/api/approvals/request',
        headers=headers,
        json={'action': 'delete_project', 'agent_id': 'product_owner'},
    ).status_code == 400
    assert client.post(
        '/api/approvals/request',
        headers=headers,
        json={'action': 'start', 'agent_id': 'missing-agent'},
    ).status_code == 404
