let agents = [];
let currentRun = null;
let ws = null;

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function headers() {
  const h = {};
  const key = document.getElementById('apiKey').value;
  const token = document.getElementById('token').value;
  if (token) h.Authorization = `Bearer ${token}`;
  if (key) h['x-api-key'] = key;
  return h;
}

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { ...headers(), ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`${response.status}`);
  return response.json();
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
      <div class="flow-node ${statusClass}">
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
      return `<article class="agent-card ${status}">
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
        ` : '<div class="idle-line">Standing by</div>'}
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
    return `<div class="collab-card">
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

function renderRun() {
  if (!currentRun) return;
  document.getElementById('runProgress').textContent = `${currentRun.progress}%`;
  document.getElementById('runStatus').textContent = currentRun.status;
  renderAgents();
  renderCollaboration();
  renderFlowDiagram();
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
  const key = document.getElementById('apiKey').value;
  const token = document.getElementById('token').value;
  const query = token ? `?token=${encodeURIComponent(token)}` : (key ? `?api_key=${encodeURIComponent(key)}` : '');
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

async function submitRequirement() {
  const inputEl = document.getElementById('chatInput');
  const chatHistory = document.getElementById('chatHistory');
  const reqText = (inputEl.value || '').trim();
  if (!reqText) return;

  // Append Executive user message to chat UI
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-msg user';
  userMsg.innerHTML = `<div class="chat-role">EXECUTIVE BUSINESS PARTNER</div><div class="chat-text">${escapeHtml(reqText)}</div>`;
  chatHistory.appendChild(userMsg);
  inputEl.value = '';

  try {
    const run = await api('/api/workflows', {
      method: 'POST',
      body: JSON.stringify({ objective: reqText, provision: true }),
      headers: { 'Content-Type': 'application/json' }
    });
    currentRun = run;
    renderRun();
    renderTimeline();

    const ackMsg = document.createElement('div');
    ackMsg.className = 'chat-msg ack';
    ackMsg.innerHTML = `<div class="chat-role">Product Owner & Project Manager</div><div class="chat-text">Requirement received. Decomposing tasks and delegating to Platform Architect, Security Architect, DevOps, QA, and SRE. Workflow Run ID: <code>${escapeHtml(run.id)}</code>.</div>`;
    chatHistory.appendChild(ackMsg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  } catch (err) {
    const errMsg = document.createElement('div');
    errMsg.className = 'chat-msg error';
    errMsg.innerHTML = `<div class="chat-role">SYSTEM ERROR</div><div class="chat-text">Could not submit requirement. Please ensure you are connected with an operator or admin API key/token.</div>`;
    chatHistory.appendChild(errMsg);
  }
}

document.getElementById('connect').addEventListener('click', connect);
const connBtn = document.getElementById('connectBtn');
if (connBtn) connBtn.addEventListener('click', connect);
document.getElementById('sendChatBtn').addEventListener('click', submitRequirement);
document.getElementById('chatInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') submitRequirement();
});
