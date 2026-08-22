let ws, agents = [], currentRun = null;
const headers = () => { const result = {}; const key = document.getElementById('apiKey').value; const token = document.getElementById('token').value; if (key) result['x-api-key'] = key; if (token) result.authorization = `Bearer ${token}`; return result; };
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[char]));

async function api(path, options = {}) { const response = await fetch(path, {...options, headers: {...headers(), ...(options.headers || {})}}); if (!response.ok) throw new Error(`${response.status}`); return response.json(); }
function renderAgents() {
  const taskMap = Object.fromEntries((currentRun?.tasks || []).map(task => [task.agent_id, task]));

  // Group agents by team
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
}

function renderTimeline() {
  document.getElementById('timeline').innerHTML = (currentRun?.events || [])
    .filter(e => e.type !== 'collaboration_message')
    .slice(-10)
    .reverse()
    .map(event => `<div class="event"><span class="event-dot"></span><div><b>${escapeHtml(event.type.replaceAll('_', ' '))}</b><small>${new Date(event.run.updated_at).toLocaleTimeString()}</small></div></div>`).join('') || '<p class="muted">Launch a workflow to see governed handoffs.</p>';
}
async function loadData() { [agents, currentRun] = await Promise.all([api('/api/agents'), api('/api/workflows').then(runs => runs.at(-1) || null)]); const models = await api('/api/models'); document.getElementById('modelCount').textContent = models.length; document.getElementById('models').innerHTML = models.map(model => `<div class="model"><span class="model-dot"></span><div><b>${escapeHtml(model.policy)}</b><small>${escapeHtml(model.model)}</small></div></div>`).join(''); renderRun(); renderTimeline(); }
function connect() { const key = document.getElementById('apiKey').value; const token = document.getElementById('token').value; const query = token ? `?token=${encodeURIComponent(token)}` : (key ? `?api_key=${encodeURIComponent(key)}` : ''); if (ws) ws.close(); ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/agents${query}`); ws.onopen = () => { document.getElementById('connectionDot').classList.add('online'); document.getElementById('connectionText').textContent = 'Live'; loadData().catch(() => {}); }; ws.onclose = () => { document.getElementById('connectionDot').classList.remove('online'); document.getElementById('connectionText').textContent = 'Disconnected'; }; ws.onmessage = event => { const message = JSON.parse(event.data); if (message.run) { currentRun = message.run; renderRun(); renderTimeline(); } }; }
document.getElementById('connect').addEventListener('click', connect);
if (document.getElementById('connectBtnHeader')) {
  document.getElementById('connectBtnHeader').addEventListener('click', connect);
}

async function submitRequirement(reqText) {
  const text = reqText || document.getElementById('chatInput')?.value?.trim();
  if (!text) return;

  const historyEl = document.getElementById('chatHistory');
  if (historyEl) {
    historyEl.innerHTML += `<div class="chat-bubble user">
      <span class="chat-author">Executive Business Partner</span>
      <p>${escapeHtml(text)}</p>
    </div>`;
    historyEl.scrollTop = historyEl.scrollHeight;
  }

  if (document.getElementById('chatInput')) {
    document.getElementById('chatInput').value = '';
  }

  try {
    currentRun = await api('/api/workflows', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({objective: text})
    });

    if (historyEl) {
      historyEl.innerHTML += `<div class="chat-bubble po">
        <span class="chat-author">Product Owner & Project Manager</span>
        <p>Requirement accepted! Initiating task graph decomposition and multi-agent team alignment for: <i>"${escapeHtml(text)}"</i>.</p>
      </div>`;
      historyEl.scrollTop = historyEl.scrollHeight;
    }

    renderRun();
    renderTimeline();
  } catch (error) {
    if (historyEl) {
      historyEl.innerHTML += `<div class="chat-bubble error">
        <span class="chat-author">System Error</span>
        <p>Could not submit requirement. Please ensure you are connected with an operator or admin API key/token.</p>
      </div>`;
      historyEl.scrollTop = historyEl.scrollHeight;
    }
  }
}

const sendChatBtn = document.getElementById('sendChatBtn');
if (sendChatBtn) {
  sendChatBtn.addEventListener('click', () => submitRequirement());
}
const chatInput = document.getElementById('chatInput');
if (chatInput) {
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitRequirement();
  });
}

