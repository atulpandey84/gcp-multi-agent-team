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
    const locText = task.model_location ? `${escapeHtml(task.executed_model || task.model_policy)} (${escapeHtml(task.model_provider || 'NVIDIA')} @ ${escapeHtml(task.model_location)})` : `${escapeHtml(task.model_policy)} (NVIDIA NIM Cloud)`;
    traceBox.innerHTML = `
      <div class="trace-item"><b>[Agent Persona]</b> ${escapeHtml(agent.role)} (${escapeHtml(agent.team)})</div>
      <div class="trace-item"><b>[Model & Host Location]</b> <span class="badge model-badge">${locText}</span></div>
      <div class="trace-item"><b>[Task Objective]</b> ${escapeHtml(task.title)}</div>
      <div class="trace-item"><b>[Live Dynamic Reasoning Status]</b> <b>${escapeHtml(task.reasoning_status || 'In Progress')}</b></div>
      ${task.failure_reason ? `
        <div class="failure-callout">
          <div class="fail-title">⚠️ Task Failure Reason</div>
          <div class="fail-reason">${escapeHtml(task.failure_reason)}</div>
          <div class="fail-resolution"><b>Suggested Resolution:</b> ${escapeHtml(task.suggested_resolution || 'Review configuration and retry.')}</div>
        </div>
      ` : ''}
      ${task.output_summary ? `<div class="trace-item summary"><b>[Summary]</b> ${escapeHtml(task.output_summary)}</div>` : ''}
    `;
  } else {
    traceBox.innerHTML = `<p class="muted">Agent ${escapeHtml(agent.role)} is standing by in active readiness state.</p>`;
  }

  const artifactBox = document.getElementById('modalOutputArtifact');
  if (task?.output_artifact || task?.document_content) {
    const docPath = task.output_artifact ? `/${task.output_artifact}` : '#';
    artifactBox.innerHTML = `
      ${task.document_title ? `<div style="font-weight:700; margin-bottom:0.4rem;">${escapeHtml(task.document_title)}</div>` : ''}
      <div class="approval-doc-box">${escapeHtml(task.document_content || 'Artifact saved: ' + task.output_artifact)}</div>

      <div style="margin-bottom:0.75rem;">
        <a href="${docPath}" target="_blank" class="task-doc-link">📄 View / Download Complete Document Artifact</a>
      </div>

      ${task.status === 'awaiting_approval' ? `
        <div class="approval-card">
          <div class="approval-head">
            <span class="approval-title">✋ Formal Document Review & Approval Required</span>
            <span class="badge warning">AWAITING APPROVAL</span>
          </div>
          <div class="approval-actions">
            <input id="modalFeedbackInput" class="feedback-input" placeholder="Feedback or rejection reason..." />
            <button onclick="approveTask('${task.id}')" class="btn-task-approve">Approve & Proceed</button>
            <button onclick="rejectTask('${task.id}')" class="btn-task-redo">Redo (Reject with Feedback)</button>
          </div>
        </div>
      ` : ''}
    `;
  } else {
    artifactBox.innerHTML = '<span class="muted">No output artifact generated for this step yet.</span>';
  }

  document.getElementById('agentDetailModal').classList.remove('hidden');
}

async function approveTask(taskId) {
  if (!currentRun) return;
  try {
    await api(`/api/workflows/${currentRun.id}/tasks/${taskId}/approve`, { method: 'POST' });
    closeAgentModal();
    await loadData();
  } catch (err) {
    alert(`Could not approve task: ${err.message}`);
  }
}

async function rejectTask(taskId) {
  if (!currentRun) return;
  const inputEl = document.getElementById('modalFeedbackInput');
  const feedback = inputEl ? inputEl.value.trim() : '';
  if (!feedback) {
    alert('Please enter a feedback comment / rejection reason before rejecting.');
    return;
  }
  try {
    await api(`/api/workflows/${currentRun.id}/tasks/${taskId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comment: feedback }),
      headers: { 'Content-Type': 'application/json' }
    });
    closeAgentModal();
    await loadData();
  } catch (err) {
    alert(`Could not reject task: ${err.message}`);
  }
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
    const hasFailed = stageTasks.some(t => t.status === 'failed');
    const isCompleted = stageTasks.length > 0 && stageTasks.every(t => t.status === 'completed');
    const isRunning = stageTasks.some(t => t.status === 'running');
    const statusClass = hasFailed ? 'failed' : (isCompleted ? 'completed' : (isRunning ? 'running' : (progress > 0 && idx === 0 ? 'completed' : 'pending')));

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
    const statusClass = task.status === 'completed' ? 'completed' : (task.status === 'failed' ? 'failed' : (task.status === 'running' ? 'running' : 'pending'));
    const agent = agents.find(a => a.id === task.agent_id) || { role: task.agent_id };

    return `
      <div class="waterfall-row" onclick="openAgentModal('${task.agent_id}')">
        <div class="waterfall-agent">
          <span class="avatar">${escapeHtml(agent.role.slice(0, 2).toUpperCase())}</span>
          <b>${escapeHtml(agent.role)}</b>
        </div>
        <div class="waterfall-track">
          <div class="waterfall-bar ${statusClass}" style="left: ${(idx / tasks.length) * 80}%; width: ${Math.max(task.progress, 15)}%;">
            <span class="waterfall-text">${escapeHtml(task.title)} ${task.status === 'failed' ? '❌ FAILED' : `(${task.progress}%)`}</span>
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
      const hostLabel = task?.model_location ? (task.model_location.includes('NVIDIA') ? 'NVIDIA Cloud' : task.model_location) : 'NVIDIA Cloud';

      let barColor = 'grey';
      let progressVal = 0;
      let reasonText = 'Queued';

      if (task) {
        progressVal = task.progress || 0;
        reasonText = task.reasoning_status || (task.status === 'completed' ? 'Completed & Validated' : 'In Progress');
        if (task.status === 'completed') {
          barColor = 'green';
        } else if (task.status === 'failed') {
          barColor = 'red';
        } else if (task.status === 'running' || task.status === 'awaiting_approval' || progressVal > 0) {
          barColor = 'amber';
        }
      }

      return `<article class="agent-card ${status}" onclick="openAgentModal('${agent.id}')">
        <div class="agent-top">
          <span class="avatar">${escapeHtml(agent.role?.slice(0, 2).toUpperCase())}</span>
          <span class="status ${status}">${status}</span>
        </div>
        <h3>${escapeHtml(agent.role)}</h3>
        <p class="mission">${escapeHtml(task?.title || agent.mission)}</p>
        ${task ? `
          <div class="task-label">
            <span class="badge model-badge">${escapeHtml(task.model_policy)} @ ${escapeHtml(hostLabel)}</span>
            <b>${progressVal}%</b>
          </div>
          <div class="bar-container">
            <div class="bar-fill ${barColor}" style="width:${Math.max(progressVal, 5)}%"></div>
            <div class="bar-overlay-text">${escapeHtml(reasonText)}</div>
          </div>
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

  const approveBtn = document.getElementById('approveExecutionBtn');
  if (approveBtn) {
    if (currentRun.status === 'running' || currentRun.status === 'paused_awaiting_approval' || currentRun.progress > 0) {
      approveBtn.disabled = true;
      approveBtn.style.opacity = '0.5';
      approveBtn.style.cursor = 'not-allowed';
      approveBtn.textContent = 'Execution In Progress';
    } else {
      approveBtn.disabled = false;
      approveBtn.style.opacity = '1';
      approveBtn.style.cursor = 'pointer';
      approveBtn.textContent = 'Approve & Initiate Engineering Execution';
    }
  }

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

function getSavedRunId() {
  return localStorage.getItem('active_run_id') || null;
}

function saveRunId(id) {
  if (id) {
    localStorage.setItem('active_run_id', id);
  } else {
    localStorage.removeItem('active_run_id');
  }
}

function saveChatHistory() {
  const chatEl = document.getElementById('chatHistory');
  if (chatEl) {
    localStorage.setItem('chat_history_html', chatEl.innerHTML);
  }
}

function restoreChatHistory() {
  const chatEl = document.getElementById('chatHistory');
  const savedHtml = localStorage.getItem('chat_history_html');
  if (chatEl && savedHtml) {
    chatEl.innerHTML = savedHtml;
  }
}

async function loadData() {
  restoreChatHistory();
  const savedRunId = getSavedRunId();

  [agents, currentRun] = await Promise.all([
    api('/api/agents'),
    savedRunId
      ? api(`/api/workflows/${savedRunId}`).catch(() => api('/api/workflows').then(runs => runs.at(-1) || null))
      : api('/api/workflows').then(runs => runs.at(-1) || null)
  ]);

  if (currentRun?.id) {
    saveRunId(currentRun.id);
  }

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

  const userMsg = document.createElement('div');
  userMsg.className = 'chat-msg user';
  userMsg.innerHTML = `<div class="chat-role">EXECUTIVE BUSINESS PARTNER</div><div class="chat-text">${escapeHtml(reqText)}</div>`;
  chatHistory.appendChild(userMsg);
  inputEl.value = '';
  saveChatHistory();

  const thinkingMsg = document.createElement('div');
  thinkingMsg.className = 'chat-msg ack';
  thinkingMsg.innerHTML = `<div class="chat-role">Product Owner & Project Manager Agents</div><div class="chat-text"><i>Evaluating requirement and aligning agent scope...</i></div>`;
  chatHistory.appendChild(thinkingMsg);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const data = await api('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: reqText }),
      headers: { 'Content-Type': 'application/json' }
    });

    thinkingMsg.remove();
    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'chat-msg ack';
    assistantMsg.innerHTML = `<div class="chat-role">Product Owner & Project Manager Agents</div><div class="chat-text">${escapeHtml(data.response || data.frozen_objective || reqText)}</div>`;
    chatHistory.appendChild(assistantMsg);

    if (data.frozen_objective) {
      pendingRequirement = data.frozen_objective;
    } else {
      pendingRequirement = reqText;
    }
    saveChatHistory();
  } catch (err) {
    thinkingMsg.remove();
    const errMsg = document.createElement('div');
    errMsg.className = 'chat-msg ack';
    errMsg.innerHTML = `<div class="chat-role">Product Owner & Project Manager Agents</div><div class="chat-text">Requirement processed: <b>${escapeHtml(reqText)}</b>. Scope aligned with Solution Architecture for Landing Zone hardening. Click <b>Approve & Initiate Engineering Execution</b> to proceed.</div>`;
    chatHistory.appendChild(errMsg);
    pendingRequirement = reqText;
    saveChatHistory();
  }
  chatHistory.scrollTop = chatHistory.scrollHeight;
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

async function continueWorkflow() {
  if (!currentRun) return;
  const chatHistory = document.getElementById('chatHistory');
  try {
    await api(`/api/workflows/${currentRun.id}/continue`, { method: 'POST' });
    const msg = document.createElement('div');
    msg.className = 'chat-msg system';
    msg.innerHTML = `<div class="chat-role">WORKFLOW CONTROL</div><div class="chat-text">Continuing execution from the last pending step for Run ID <code>${escapeHtml(currentRun.id)}</code>...</div>`;
    chatHistory.appendChild(msg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    await loadData();
  } catch (err) {
    alert(`Could not continue workflow: ${err.message}`);
  }
}

async function startFreshWorkflow() {
  if (!currentRun) return;
  const chatHistory = document.getElementById('chatHistory');
  try {
    await api(`/api/workflows/${currentRun.id}/start_fresh`, { method: 'POST' });
    const msg = document.createElement('div');
    msg.className = 'chat-msg system';
    msg.innerHTML = `<div class="chat-role">WORKFLOW CONTROL</div><div class="chat-text">Started fresh execution from Step 1 for Run ID <code>${escapeHtml(currentRun.id)}</code>...</div>`;
    chatHistory.appendChild(msg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    await loadData();
  } catch (err) {
    alert(`Could not start fresh workflow: ${err.message}`);
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
const continueBtn = document.getElementById('continueRunBtn');
if (continueBtn) continueBtn.addEventListener('click', continueWorkflow);
const freshBtn = document.getElementById('startFreshBtn');
if (freshBtn) freshBtn.addEventListener('click', startFreshWorkflow);
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
