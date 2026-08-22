let agents = [];
let currentRun = null;
let ws = null;
let logs = [];
let pendingRequirement = "I want a full fledged architecturally secure and hardened GCP landing zone";

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function getSavedApiKey() {
  return localStorage.getItem('monitoring_api_key') || '';
}

function saveApiKey(key) {
  if (key) {
    localStorage.setItem('monitoring_api_key', key);
  } else {
    localStorage.removeItem('monitoring_api_key');
  }
}

function headers() {
  const h = {};
  const key = document.getElementById('apiKey').value || getSavedApiKey();
  if (key) {
    if (key.startsWith('ey') || key.length > 50) {
      h.Authorization = `Bearer ${key}`;
    } else {
      h['x-api-key'] = key;
    }
  }
  return h;
}

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { ...headers(), ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`${response.status}`);
  return response.json();
}

function openAgentModal(agentId) {
  const agent = agents.find(a => a.id === agentId) || { id: agentId, role: agentId, team: 'Agent', mission: 'Autonomous Specialist' };
  const task = (currentRun?.tasks || []).find(t => t.agent_id === agentId);

  document.getElementById('modalAgentRole').textContent = agent.role;
  document.getElementById('modalAgentTeam').textContent = `${agent.team || 'Engineering'} Team`;
  document.getElementById('modalAgentMission').textContent = task?.title || agent.mission;
  document.getElementById('modalModelPolicy').textContent = task?.model_policy || agent.model_policy || 'senior_reasoning';

  const status = task?.status === 'running' ? 'working' : (task?.status || agent.status || 'idle');
  const statusEl = document.getElementById('modalAgentStatus');
  statusEl.textContent = status.toUpperCase();
  statusEl.className = `status ${status}`;

  const traceBox = document.getElementById('modalThinkingTrace');
  if (task) {
    traceBox.innerHTML = `
      <div class="trace-item"><b>[Agent Persona]</b> ${escapeHtml(agent.role)} (${escapeHtml(agent.team)})</div>
      <div class="trace-item"><b>[Model Policy]</b> Using ${escapeHtml(task.model_policy)} model tier for reasoning</div>
      <div class="trace-item"><b>[Task Objective]</b> ${escapeHtml(task.title)}</div>
      <div class="trace-item"><b>[Reasoning Status]</b> ${task.status === 'completed' ? '✓ Reasoning & output generation complete (100%)' : '⚙ Active reasoning & decomposition in progress...'}</div>
      ${task.output_summary ? `<div class="trace-item summary"><b>[Summary]</b> ${escapeHtml(task.output_summary)}</div>` : ''}
    `;
  } else {
    traceBox.innerHTML = `<p class="muted">Agent ${escapeHtml(agent.role)} is standing by in active readiness state.</p>`;
  }

  const artifactBox = document.getElementById('modalOutputArtifact');
  if (task?.output_artifact) {
    artifactBox.innerHTML = `<code>${escapeHtml(task.output_artifact)}</code>`;
  } else {
    artifactBox.innerHTML = '<span class="muted">No output artifact generated for this step yet.</span>';
  }

  document.getElementById('agentDetailModal').classList.remove('hidden');
}

function closeAgentModal() {
  document.getElementById('agentDetailModal').classList.add('hidden');
}

function renderFlowDiagram() {
  const flowContainer = document.getElementById('workflowFlowDiagram');
  if (!flowContainer) return;

  const stages = [
    { id: 'product', name: 'Product & PM', desc: 'Requirements & Scope', agents: ['product_owner', 'project_manager'] },
    { id: 'architecture', name: 'Architecture', desc: 'Platform & Solution Design', agents: ['platform_architect', 'solution_architect'] },
    { id: 'security_finops', name: 'Security & FinOps', desc: 'Threat Model & Cost', agents: ['security_architect', 'finops_engineer'] },
    { id: 'devops_impl', name: 'DevOps & Dev', desc: 'IaC & Implementation', agents: ['devops_lead', 'cloud_infrastructure_engineer', 'backend_engineer'] },
    { id: 'qa_nfr', name: 'QA & Testing', desc: 'Quality & NFR Gates', agents: ['qa_lead', 'test_automation_engineer', 'nfr_test_engineer'] },
    { id: 'operations', name: 'Operations & SRE', desc: 'Readiness & Production', agents: ['application_management_lead', 'sre_observability_engineer', 'production_reliability_engineer'] }
  ];

  const tasksMap = Object.fromEntries((currentRun?.tasks || []).map(t => [t.agent_id, t]));
  const progress = currentRun?.progress || 0;

  const html = stages.map((stage, idx) => {
    const stageTasks = stage.agents.map(aid => tasksMap[aid]).filter(Boolean);
    const isCompleted = stageTasks.length > 0 && stageTasks.every(t => t.status === 'completed');
    const isRunning = stageTasks.some(t => t.status === 'running');
    const statusClass = isCompleted ? 'completed' : (isRunning ? 'running' : (progress > 0 && idx === 0 ? 'completed' : 'pending'));

    return `
      <div class="flow-node ${statusClass}" onclick="openAgentModal('${stage.agents[0]}')">
        <div class="flow-step-num">Stage ${idx + 1}</div>
        <div class="flow-node-title">${escapeHtml(stage.name)}</div>
        <div class="flow-node-desc">${escapeHtml(stage.desc)}</div>
        <div class="flow-node-status">${statusClass.toUpperCase()}</div>
      </div>
      ${idx < stages.length - 1 ? '<div class="flow-arrow">➔</div>' : ''}
    `;
  }).join('');

  flowContainer.innerHTML = html;
}

function renderWaterfall() {
  const waterfallEl = document.getElementById('waterfallContainer');
  if (!waterfallEl) return;
  const tasks = currentRun?.tasks || [];

  if (tasks.length === 0) {
    waterfallEl.innerHTML = '<p class="muted">Launch or approve execution to display the waterfall timeline graph.</p>';
    return;
  }

  const html = tasks.map((task, idx) => {
    const statusClass = task.status === 'completed' ? 'completed' : (task.status === 'running' ? 'running' : 'pending');
    const agent = agents.find(a => a.id === task.agent_id) || { role: task.agent_id };

    return `
      <div class="waterfall-row" onclick="openAgentModal('${task.agent_id}')">
        <div class="waterfall-agent">
          <span class="avatar">${escapeHtml(agent.role.slice(0, 2).toUpperCase())}</span>
          <b>${escapeHtml(agent.role)}</b>
        </div>
        <div class="waterfall-track">
          <div class="waterfall-bar ${statusClass}" style="left: ${(idx / tasks.length) * 80}%; width: ${Math.max(task.progress, 15)}%;">
            <span class="waterfall-text">${escapeHtml(task.title)} (${task.progress}%)</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  waterfallEl.innerHTML = html;
}

function renderArtifacts() {
  const artifactEl = document.getElementById('artifactList');
  if (!artifactEl) return;
  const artifacts = currentRun?.artifacts || [];

  if (artifacts.length === 0) {
    artifactEl.innerHTML = '<p class="muted">No background artifacts produced yet.</p>';
    return;
  }

  artifactEl.innerHTML = artifacts.map(art => `
    <div class="artifact-badge">
      <span class="artifact-icon">📄</span>
      <span class="artifact-name">${escapeHtml(art)}</span>
      <span class="artifact-status">VERIFIED</span>
    </div>
  `).join('');
}

function renderAgents() {
  const taskMap = Object.fromEntries((currentRun?.tasks || []).map(task => [task.agent_id, task]));

  const teams = {};
  agents.forEach(agent => {
    const teamName = agent.team || 'Unassigned';
    if (!teams[teamName]) teams[teamName] = [];
    teams[teamName].push(agent);
  });

  const teamsHtml = Object.entries(teams).map(([teamName, teamAgents]) => {
    const cardsHtml = teamAgents.map(agent => {
      const task = taskMap[agent.id];
      const status = task?.status === 'running' ? 'working' : (task?.status || agent.status || 'idle');
      return `<article class="agent-card ${status}" onclick="openAgentModal('${agent.id}')">
        <div class="agent-top">
          <span class="avatar">${escapeHtml(agent.role?.slice(0, 2).toUpperCase())}</span>
          <span class="status ${status}">${status}</span>
        </div>
        <h3>${escapeHtml(agent.role)}</h3>
        <p class="mission">${escapeHtml(task?.title || agent.mission)}</p>
        ${task ? `
          <div class="task-label">
            <span class="badge model-badge">${escapeHtml(task.model_policy)}</span>
            <b>${task.progress}%</b>
          </div>
          <div class="bar"><i style="width:${task.progress}%"></i></div>
          ${task.output_summary ? `<div class="output-snippet">✓ ${escapeHtml(task.output_summary)}</div>` : ''}
        ` : '<div class="idle-line">Standing by - Click to drill down</div>'}
      </article>`;
    }).join('');

    return `<div class="team-group">
      <div class="team-header">
        <span class="team-title">${escapeHtml(teamName)} Team</span>
        <span class="team-count">${teamAgents.length} Agents</span>
      </div>
      <div class="agent-grid">${cardsHtml}</div>
    </div>`;
  }).join('');

  document.getElementById('teamsContainer').innerHTML = teamsHtml;
  document.getElementById('activeAgents').textContent = (currentRun?.tasks || []).filter(task => task.status === 'running').length;
}

function renderCollaboration() {
  const feedEl = document.getElementById('collaborationFeed');
  if (!feedEl) return;
  const collabEvents = (currentRun?.events || [])
    .filter(e => e.type === 'collaboration_message')
    .slice(-8)
    .reverse();

  if (collabEvents.length === 0) {
    feedEl.innerHTML = '<div class="collab-empty muted">No inter-agent handoffs yet.</div>';
    return;
  }

  feedEl.innerHTML = collabEvents.map(e => {
    const d = e.details || {};
    return `<div class="collab-card" onclick="openAgentModal('${d.sender}')">
      <div class="collab-header">
        <span class="sender">${escapeHtml(d.sender)} (${escapeHtml(d.sender_team)})</span>
        <span class="arrow">➔</span>
        <span class="receiver">${escapeHtml(d.receiver)} (${escapeHtml(d.receiver_team)})</span>
      </div>
      <div class="collab-action">${escapeHtml(d.action)}</div>
      <div class="collab-artifact">Artifact: ${escapeHtml(d.artifact)}</div>
    </div>`;
  }).join('');
}

function renderLogConsole() {
  const logEl = document.getElementById('logConsole');
  if (!logEl) return;
  const events = currentRun?.events || [];
  if (events.length === 0) {
    logEl.innerHTML = '<p class="muted">Connect to stream execution logs.</p>';
    return;
  }

  logEl.innerHTML = events.slice(-30).map(event => {
    const time = new Date(event.run?.updated_at || Date.now()).toLocaleTimeString();
    const type = event.type || 'INFO';
    const isError = type.includes('failed') || type.includes('cancelled');
    const isCompleted = type.includes('completed');
    const details = JSON.stringify(event.details || {});
    return `<div class="log-entry ${isError ? 'error' : (isCompleted ? 'completed' : '')}">
      <span class="log-time">[${escapeHtml(time)}]</span>
      <span class="log-type">[${escapeHtml(type.toUpperCase())}]</span>
      <span class="log-msg">${escapeHtml(details)}</span>
    </div>`;
  }).join('');
  logEl.scrollTop = logEl.scrollHeight;
}

function renderRun() {
  if (!currentRun) return;
  document.getElementById('runProgress').textContent = `${currentRun.progress}%`;
  document.getElementById('runStatus').textContent = currentRun.status;
  renderAgents();
  renderCollaboration();
  renderFlowDiagram();
  renderWaterfall();
  renderArtifacts();
  renderLogConsole();
}

function renderTimeline() {
  document.getElementById('timeline').innerHTML = (currentRun?.events || [])
    .filter(e => e.type !== 'collaboration_message')
    .slice(-10)
    .reverse()
    .map(event => `<div class="event"><span class="event-dot"></span><div><b>${escapeHtml(event.type.replaceAll('_', ' '))}</b><small>${new Date(event.run.updated_at).toLocaleTimeString()}</small></div></div>`).join('') || '<p class="muted">Launch a workflow to see governed handoffs.</p>';
}

async function loadData() {
  [agents, currentRun] = await Promise.all([
    api('/api/agents'),
    api('/api/workflows').then(runs => runs.at(-1) || null)
  ]);
  const models = await api('/api/models');
  document.getElementById('modelCount').textContent = models.length;
  document.getElementById('models').innerHTML = models.map(model => `
    <div class="model">
      <span class="model-dot"></span>
      <div><b>${escapeHtml(model.policy)}</b><small>${escapeHtml(model.model)}</small></div>
    </div>
  `).join('');
  renderRun();
  renderTimeline();
}

function connect() {
  const keyInput = document.getElementById('apiKey');
  const key = keyInput.value.trim() || getSavedApiKey();
  if (keyInput.value.trim()) {
    saveApiKey(keyInput.value.trim());
  } else if (key) {
    keyInput.value = key;
  }
  const query = key ? (key.startsWith('ey') || key.length > 50 ? `?token=${encodeURIComponent(key)}` : `?api_key=${encodeURIComponent(key)}`) : '';
  if (ws) ws.close();
  ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/agents${query}`);
  ws.onopen = () => {
    document.getElementById('connectionDot').classList.add('online');
    document.getElementById('connectionText').textContent = 'Live';
    loadData().catch(() => {});
  };
  ws.onclose = () => {
    document.getElementById('connectionDot').classList.remove('online');
    document.getElementById('connectionText').textContent = 'Disconnected';
  };
  ws.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.run) {
      currentRun = message.run;
      renderRun();
      renderTimeline();
    }
  };
}

async function handleChatInput() {
  const inputEl = document.getElementById('chatInput');
  const chatHistory = document.getElementById('chatHistory');
  const reqText = (inputEl.value || '').trim();
  if (!reqText) return;

  pendingRequirement = reqText;

  const userMsg = document.createElement('div');
  userMsg.className = 'chat-msg user';
  userMsg.innerHTML = `<div class="chat-role">EXECUTIVE BUSINESS PARTNER</div><div class="chat-text">${escapeHtml(reqText)}</div>`;
  chatHistory.appendChild(userMsg);
  inputEl.value = '';

  setTimeout(() => {
    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'chat-msg ack';
    assistantMsg.innerHTML = `<div class="chat-role">Product Owner & Project Manager</div><div class="chat-text">Requirement understood: <i>"${escapeHtml(reqText)}"</i>. I have aligned with Solution Architect (DeepSeek Pro) & Security Architect to ensure complete Landing Zone hardening, Zero Trust IAM, and automated governance. Click <b>Approve & Initiate Engineering Execution</b> to proceed.</div>`;
    chatHistory.appendChild(assistantMsg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }, 400);
}

async function stopTasksAndReset() {
  const chatHistory = document.getElementById('chatHistory');
  try {
    await api('/api/workflows/stop_all', { method: 'POST' });
    const stopMsg = document.createElement('div');
    stopMsg.className = 'chat-msg system';
    stopMsg.innerHTML = `<div class="chat-role">SYSTEM CONTROL</div><div class="chat-text">Active multi-agent execution tasks stopped. Requirement session reset.</div>`;
    chatHistory.appendChild(stopMsg);

    pendingRequirement = "I want a full fledged architecturally secure and hardened GCP landing zone";
    const inputEl = document.getElementById('chatInput');
    if (inputEl) inputEl.value = '';

    await loadData();
  } catch (err) {
    const errMsg = document.createElement('div');
    errMsg.className = 'chat-msg error';
    errMsg.innerHTML = `<div class="chat-role">SYSTEM ERROR</div><div class="chat-text">Could not stop tasks: ${escapeHtml(err.message)}</div>`;
    chatHistory.appendChild(errMsg);
  }
}

async function approveAndInitiateExecution() {
  const chatHistory = document.getElementById('chatHistory');

  const approveMsg = document.createElement('div');
  approveMsg.className = 'chat-msg system';
  approveMsg.innerHTML = `<div class="chat-role">EXECUTIVE APPROVAL</div><div class="chat-text">Executive requirement approved. Triggering multi-agent execution pipeline...</div>`;
  chatHistory.appendChild(approveMsg);

  try {
    const run = await api('/api/workflows', {
      method: 'POST',
      body: JSON.stringify({ objective: pendingRequirement, provision: true }),
      headers: { 'Content-Type': 'application/json' }
    });
    currentRun = run;
    renderRun();
    renderTimeline();

    const ackMsg = document.createElement('div');
    ackMsg.className = 'chat-msg ack';
    ackMsg.innerHTML = `<div class="chat-role">Engineering Orchestrator</div><div class="chat-text">Execution started for Workflow Run ID: <code>${escapeHtml(run.id)}</code>. Generated artifacts will be persisted to <code>data/workflows/${escapeHtml(run.id)}/</code> for background review.</div>`;
    chatHistory.appendChild(ackMsg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  } catch (err) {
    const errMsg = document.createElement('div');
    errMsg.className = 'chat-msg error';
    errMsg.innerHTML = `<div class="chat-role">SYSTEM ERROR</div><div class="chat-text">Could not submit requirement. Please ensure you are connected with an operator or admin API key/token.</div>`;
    chatHistory.appendChild(errMsg);
  }
}

const connBtn = document.getElementById('connectBtn');
if (connBtn) connBtn.addEventListener('click', connect);
document.getElementById('sendChatBtn').addEventListener('click', handleChatInput);
document.getElementById('approveExecutionBtn').addEventListener('click', approveAndInitiateExecution);
document.getElementById('stopResetBtn').addEventListener('click', stopTasksAndReset);
document.getElementById('closeModalBtn').addEventListener('click', closeAgentModal);
document.getElementById('chatInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') handleChatInput();
});

// Auto-connect on page load if key saved
window.addEventListener('DOMContentLoaded', () => {
  const savedKey = getSavedApiKey();
  if (savedKey) {
    document.getElementById('apiKey').value = savedKey;
  }
  connect();
});
