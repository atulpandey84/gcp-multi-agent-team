import asyncio
import yaml
import json
from pathlib import Path
from typing import Callable
from .models import Agent
from .db import upsert_agent, get_all_agents, append_audit


class AgentRegistry:
    def __init__(self, agents_yaml: str | Path):
        self._agents: dict[str, Agent] = {}
        self._subscribers: list[Callable[[dict], None]] = []
        self._tasks: dict[str, asyncio.Task] = {}
        self._load_from_yaml(agents_yaml)

    def _load_from_yaml(self, path: str | Path):
        content = Path(path).read_text()
        data = yaml.safe_load(content) or {}
        for a in data.get("agents", []):
            if not isinstance(a, dict):
                continue
            agent = Agent(id=a["id"], role=a.get("role"), team=a.get("team"), mission=a.get("mission"))
            self._agents[agent.id] = agent
            # persist/ensure agent exists in DB
            try:
                upsert_agent(agent)
            except Exception:
                pass

    def list_agents(self):
        try:
            rows = get_all_agents()
            if rows:
                return [a.dict() for a in rows]
        except Exception:
            pass
        return [a.dict() for a in self._agents.values()]

    def get(self, agent_id: str):
        return self._agents.get(agent_id)

    def subscribe(self, cb: Callable[[dict], None]):
        self._subscribers.append(cb)

    def _notify(self, payload: dict):
        for cb in list(self._subscribers):
            try:
                cb(payload)
            except Exception:
                pass

    def start_agent(self, agent_id: str):
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        agent.status = "running"
        self._notify({"type": "status", "agent": agent.dict()})
        try:
            upsert_agent(agent)
            append_audit("start", agent_id, None)
        except Exception:
            pass
        # start a simulated task
        if agent_id in self._tasks:
            return True

        async def _worker(aid: str):
            for i in range(1, 6):
                await asyncio.sleep(2)
                self._notify({"type": "progress", "agent_id": aid, "progress": i * 20})
            self._agents[aid].status = "idle"
            self._notify({"type": "status", "agent": self._agents[aid].dict()})

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # no running event loop (tests or sync contexts); skip background worker
            return True
        task = loop.create_task(_worker(agent_id))
        self._tasks[agent_id] = task
        return True

    def stop_agent(self, agent_id: str):
        task = self._tasks.pop(agent_id, None)
        if task:
            task.cancel()
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        agent.status = "stopped"
        self._notify({"type": "status", "agent": agent.dict()})
        try:
            upsert_agent(agent)
            append_audit("stop", agent_id, None)
        except Exception:
            pass
        return True

    def assign_task(self, agent_id: str, task: dict):
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        agent.status = "busy"
        self._notify({"type": "assigned", "agent": agent.dict(), "task": task})
        # persist an audit record
        try:
            upsert_agent(agent)
            append_audit("assign", agent_id, json.dumps(task))
        except Exception:
            pass
        return True
