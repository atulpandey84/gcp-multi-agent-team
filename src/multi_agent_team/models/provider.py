"""
Multi-Model Provider for the GCP Multi-Agent Engineering Organization.

Provides concurrent access to multiple NVIDIA model instances with Ollama fallback.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
except ImportError:
    ChatNVIDIA = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]

logger = logging.getLogger(__name__)

MODEL_POLICY_AGENT_MAP = {
    "architecture_critical": ["platform_architect", "solution_architect", "security_architect"],
    "senior_reasoning": ["product_owner", "project_manager", "engineering_orchestrator", "development_lead"],
    "coding": ["backend_engineer", "frontend_engineer", "integration_engineer", "ai_automation_engineer"],
    "fast_agent": ["qa_lead", "test_automation_engineer", "nfr_test_engineer", "sre_observability_engineer"],
    "fast_coding": ["cloud_infrastructure_engineer", "devops_lead", "cicd_engineer", "finops_engineer"],
    "embedding": ["knowledge_retriever"],
    "reranker": ["knowledge_retriever"],
}


@dataclass
class ModelInvocation:
    invocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy: str = ""
    model_name: str = ""
    provider: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success: bool = True
    error: Optional[str] = None
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None


@dataclass
class ModelStats:
    total_invocations: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[str] = None


def _load_active_models() -> dict:
    active_path = ROOT / "config" / "models_active.yaml"
    source_path = active_path if active_path.exists() else (ROOT / "config" / "models.yaml")
    with source_path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("models", {})


def fetch_ollama_tags(url: str) -> list[str]:
    try:
        import urllib.request
        req = urllib.request.Request(f"{url}/api/tags", headers={'User-Agent': 'MultiAgent/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                import json
                body = json.loads(resp.read().decode('utf-8'))
                models = body.get("models", [])
                return [m.get("name", "") for m in models if isinstance(m, dict)]
    except Exception:
        pass
    return []


def trigger_ollama_pull(url: str, model_name: str) -> bool:
    try:
        import urllib.request
        import json
        data = json.dumps({"name": model_name, "stream": False}).encode("utf-8")
        req = urllib.request.Request(f"{url}/api/pull", data=data, headers={"Content-Type": "application/json", "User-Agent": "MultiAgent/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as exc:
        logger.warning(f"Auto-download model {model_name} failed on host {url}: {exc}")
        return False


def select_best_ollama_instance() -> dict:
    local_url = os.getenv("OLLAMA_LOCAL_URL", "http://192.168.31.135:11434").rstrip("/")
    remote_url = os.getenv("OLLAMA_REMOTE_URL", "http://192.168.31.63:11434").rstrip("/")

    candidates = [
        {"url": local_url, "label": f"Local GPU/CPU ({local_url.replace('http://', '')})", "is_gpu": True, "score": 0, "available_models": []},
        {"url": remote_url, "label": f"Remote CPU ({remote_url.replace('http://', '')})", "is_gpu": False, "score": 0, "available_models": []},
    ]

    best = None
    best_score = -999

    for cand in candidates:
        try:
            start = time.time()
            models = fetch_ollama_tags(cand["url"])
            elapsed = time.time() - start
            cand["available_models"] = models
            score = 100 - (elapsed * 20)
            if cand["is_gpu"]:
                score += 30
            cand["score"] = score
            if score > best_score:
                best_score = score
                best = cand
        except Exception as exc:
            logger.warning(f"Ollama instance {cand['url']} unreachable: {exc}")

    return best or candidates[0]


class MockModel:
    """Mock model for demo/testing when no real model provider is available.
    
    Returns structured, plausible responses based on the prompt content
    so the full agent pipeline can execute without NVIDIA API or Ollama.
    """

    def __init__(self, policy: str):
        self.policy = policy
        self.model_name = f"mock-{policy}"
        self.provider = "Mock (demo mode)"
        self._stats = ModelStats()

    def invoke(self, prompt: str, **kwargs) -> Any:
        """Return a mock response based on prompt content."""
        import time

        start = time.time()
        response = self._generate_mock_response(prompt)
        latency_ms = (time.time() - start) * 1000

        # Create a mock result object with response_metadata
        class _MockResult:
            def __init__(self, content, metadata):
                self.content = content
                self.response_metadata = metadata

        result = _MockResult(
            str(response),
            {
                "model_provider": self.provider,
                "model_name": self.model_name,
                "model_location": "Local (mock)",
                "policy": self.policy,
                "latency_ms": latency_ms,
                "mock": True,
            },
        )

        self._stats.total_invocations += 1
        self._stats.success_count += 1
        self._stats.total_latency_ms += latency_ms
        self._stats.last_used = datetime.now(timezone.utc).isoformat()
        return result

    def _generate_mock_response(self, prompt: str) -> Dict[str, Any]:
        """Generate a context-aware mock response."""
        prompt_lower = prompt.lower()

        # Detect the type of request from prompt content
        if "architecture" in prompt_lower or "platform" in prompt_lower:
            return {
                "status": "mock_architecture_designed",
                "components": ["resource_hierarchy", "network_design", "iam_model"],
                "recommendations": [
                    "Use shared VPC for network isolation",
                    "Enable VPC Service Controls",
                    "Implement least-privilege IAM",
                ],
                "mock": True,
            }
        elif "security" in prompt_lower or "threat" in prompt_lower:
            return {
                "status": "mock_security_reviewed",
                "threat_model": {"id": "TM-MOCK", "risks": ["Data exposure", "Unauthorized access"]},
                "controls": [
                    "Encryption at rest and in transit",
                    "IAM least privilege",
                    "Audit logging",
                ],
                "mock": True,
            }
        elif "requirement" in prompt_lower or "product" in prompt_lower:
            return {
                "status": "mock_requirements_defined",
                "requirements": ["REQ-001: GCP Landing Zone environment"],
                "acceptance_criteria": ["Environment provisioned", "Security controls applied"],
                "epics": ["Epic-1: Infrastructure provisioning"],
                "mock": True,
            }
        elif "cost" in prompt_lower or "finops" in prompt_lower:
            return {
                "status": "mock_cost_analyzed",
                "monthly_cost_estimate": 1250.00,
                "budget_status": "within_budget",
                "optimizations": ["Right-size VMs", "Use committed use discounts"],
                "mock": True,
            }
        elif "test" in prompt_lower or "qa" in prompt_lower:
            return {
                "status": "mock_tests_executed",
                "test_coverage": 85.0,
                "tests_passed": 42,
                "tests_failed": 0,
                "mock": True,
            }
        elif "deploy" in prompt_lower or "devops" in prompt_lower or "pipeline" in prompt_lower:
            return {
                "status": "mock_deployment_ready",
                "pipeline_status": "ready",
                "rollback_available": True,
                "environments": ["development", "staging"],
                "mock": True,
            }
        elif "monitor" in prompt_lower or "sre" in prompt_lower or "observability" in prompt_lower:
            return {
                "status": "mock_observability_configured",
                "slo": "99.9%",
                "alerts_configured": True,
                "dashboards": ["infrastructure", "application"],
                "mock": True,
            }
        elif "code" in prompt_lower or "implement" in prompt_lower or "backend" in prompt_lower or "frontend" in prompt_lower:
            return {
                "status": "mock_code_implemented",
                "files_created": ["main.py", "utils.py", "tests.py"],
                "tests_passed": True,
                "mock": True,
            }
        else:
            return {
                "status": "mock_response",
                "summary": "Mock response generated (no real model provider available)",
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "mock": True,
            }

    async def ainvoke(self, prompt: str, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, prompt, **kwargs)


class SmartFallbackModel:
    """Wraps a primary NVIDIA model with Ollama fallback on failure."""

    def __init__(self, policy: str, primary_model: Any, cfg: dict):
        self.policy = policy
        self.primary = primary_model
        self.cfg = cfg
        self.model_name = cfg.get("model", "unknown")
        self.provider = "NVIDIA Cloud Endpoints"
        self.temperature = cfg.get("temperature", 0.1)
        self.max_tokens = cfg.get("max_tokens", cfg.get("max_completion_tokens", 4096))
        self.timeout = cfg.get("timeout", int(os.getenv("MODEL_TIMEOUT", "120")))
        self._stats = ModelStats()

    def invoke(self, prompt: str, **kwargs) -> Any:
        max_retries = int(os.getenv("NVIDIA_MAX_RETRIES", "3"))
        last_error = ""
        for attempt in range(max_retries):
            try:
                start = time.time()
                res = self.primary.invoke(prompt, **kwargs)
                latency_ms = (time.time() - start) * 1000
                if hasattr(res, "response_metadata"):
                    res.response_metadata["model_provider"] = self.provider
                    res.response_metadata["model_name"] = self.model_name
                    res.response_metadata["model_location"] = "NVIDIA Cloud Endpoints"
                    res.response_metadata["policy"] = self.policy
                    res.response_metadata["latency_ms"] = latency_ms
                self._record_stats(success=True, latency_ms=latency_ms)
                return res
            except Exception as exc:
                last_error = str(exc)
                logger.warning(f"NVIDIA API attempt {attempt + 1}/{max_retries} failed for policy {self.policy}: {exc}")
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))

        logger.warning(f"All NVIDIA API retries exhausted for policy {self.policy}. Routing to Ollama fallback...")
        return self._ollama_fallback(prompt, last_error)

    def _ollama_fallback(self, prompt: str, nvidia_err: str) -> Any:
        if ChatOllama is not None:
            try:
                ollama_inst = select_best_ollama_instance()
                target_url = ollama_inst["url"]
                requested_model = self.cfg.get("ollama_model", "llama3")
                available_models = ollama_inst.get("available_models") or fetch_ollama_tags(target_url)

                chosen_model = None
                if any(requested_model in m for m in available_models):
                    chosen_model = requested_model
                else:
                    pulled = trigger_ollama_pull(target_url, requested_model)
                    if pulled:
                        chosen_model = requested_model
                    elif available_models:
                        chosen_model = available_models[0].split(":")[0]
                        logger.info(f"Auto-pull failed. Selected alternate model '{chosen_model}' on host {target_url}.")

                if not chosen_model:
                    logger.warning(
                        f"Ollama has no suitable model for {self.policy}. Using MockModel."
                    )
                    return MockModel(self.policy).invoke(prompt)

                start = time.time()
                ollama_model = ChatOllama(base_url=target_url, model=chosen_model, temperature=self.temperature)
                res = ollama_model.invoke(prompt)
                latency_ms = (time.time() - start) * 1000
                if hasattr(res, "response_metadata"):
                    res.response_metadata["model_provider"] = f"Ollama ({chosen_model})"
                    res.response_metadata["model_name"] = chosen_model
                    res.response_metadata["model_location"] = ollama_inst["label"]
                    res.response_metadata["policy"] = self.policy
                    res.response_metadata["latency_ms"] = latency_ms
                    res.response_metadata["fallback"] = True
                self._record_stats(success=True, latency_ms=latency_ms)
                return res
            except Exception as exc:
                logger.warning(f"Ollama invocation failed: {exc}")
                return MockModel(self.policy).invoke(prompt)
        # ChatOllama is not installed - fall back to MockModel
        return MockModel(self.policy).invoke(prompt)

    def _record_stats(self, success: bool, latency_ms: float):
        self._stats.total_invocations += 1
        if success:
            self._stats.success_count += 1
            self._stats.total_latency_ms += latency_ms
        else:
            self._stats.failure_count += 1
        self._stats.last_used = datetime.now(timezone.utc).isoformat()

    def get_stats(self) -> ModelStats:
        return self._stats

    async def ainvoke(self, prompt: str, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, prompt, **kwargs)


class ModelProvider:
    def __init__(self):
        self._models: Dict[str, SmartFallbackModel] = {}
        self._invocation_history: List[ModelInvocation] = []
        self._stats_by_policy: Dict[str, ModelStats] = {}
        self._initialized = False

    def initialize(self) -> Dict[str, SmartFallbackModel]:
        if self._initialized:
            return self._models
        models_cfg = _load_active_models()
        for policy, cfg in models_cfg.items():
            try:
                timeout = cfg.get("timeout", int(os.getenv("MODEL_TIMEOUT", "120")))
                kw = {
                    "model": cfg["model"],
                    "temperature": cfg.get("temperature", 0.1),
                    "timeout": timeout,
                }
                if "max_completion_tokens" in cfg:
                    kw["max_completion_tokens"] = cfg.get("max_completion_tokens")
                else:
                    kw["max_tokens"] = cfg.get("max_tokens", 4096)
                if ChatNVIDIA is not None:
                    try:
                        nvidia_model = ChatNVIDIA(**kw)
                    except TypeError:
                        nvidia_model = ChatNVIDIA(
                            model=cfg["model"],
                            temperature=cfg.get("temperature", 0.1),
                            max_tokens=cfg.get("max_tokens", 4096),
                            timeout=timeout,
                        )
                else:
                    nvidia_model = None
                self._models[policy] = SmartFallbackModel(policy, nvidia_model, cfg)
                self._stats_by_policy[policy] = ModelStats()
                logger.info(f"Initialized model policy '{policy}': {cfg['model']}")
            except Exception as exc:
                logger.error(f"Failed to initialize model policy '{policy}': {exc}")
        self._initialized = True
        return self._models

    def get_model(self, policy: str) -> Optional[SmartFallbackModel]:
        if not self._initialized:
            self.initialize()
        return self._models.get(policy)

    def get_model_for_agent(self, agent_id: str) -> Optional[SmartFallbackModel]:
        for policy, agents in MODEL_POLICY_AGENT_MAP.items():
            if agent_id in agents:
                return self.get_model(policy)
        return self.get_model("fast_agent")

    def list_models(self) -> List[str]:
        if not self._initialized:
            self.initialize()
        return list(self._models.keys())

    async def invoke_concurrent(
        self,
        invocations: List[Dict[str, Any]],
    ) -> List[Any]:
        if not self._initialized:
            self.initialize()

        async def _single_invoke(inv: Dict[str, Any]) -> Any:
            policy = inv["policy"]
            prompt = inv["prompt"]
            agent_id = inv.get("agent_id")
            workflow_id = inv.get("workflow_id")
            kwargs = {k: v for k, v in inv.items() if k not in ("policy", "prompt", "agent_id", "workflow_id")}

            model = self.get_model(policy)
            if model is None:
                raise ValueError(f"Unknown model policy: {policy}")

            start = time.time()
            try:
                result = await model.ainvoke(prompt, **kwargs)
                latency_ms = (time.time() - start) * 1000

                model_meta = getattr(result, "response_metadata", {}) or {}
                invocation = ModelInvocation(
                    policy=policy,
                    model_name=model_meta.get("model_name", model.model_name),
                    provider=model_meta.get("model_provider", model.provider),
                    latency_ms=latency_ms,
                    success=True,
                    agent_id=agent_id,
                    workflow_id=workflow_id,
                )
                if hasattr(result, "usage_metadata"):
                    inv_tokens = result.usage_metadata
                    invocation.prompt_tokens = inv_tokens.get("input_tokens", 0)
                    invocation.completion_tokens = inv_tokens.get("output_tokens", 0)
                    invocation.total_tokens = invocation.prompt_tokens + invocation.completion_tokens

                self._invocation_history.append(invocation)
                self._stats_by_policy[policy] = model.get_stats()
                return result
            except Exception as exc:
                latency_ms = (time.time() - start) * 1000
                invocation = ModelInvocation(
                    policy=policy,
                    model_name=model.model_name if model else "unknown",
                    provider=model.provider if model else "unknown",
                    latency_ms=latency_ms,
                    success=False,
                    error=str(exc),
                    agent_id=agent_id,
                    workflow_id=workflow_id,
                )
                self._invocation_history.append(invocation)
                raise

        results = await asyncio.gather(*[_single_invoke(inv) for inv in invocations], return_exceptions=True)
        return results

    def get_invocation_history(self) -> List[ModelInvocation]:
        return list(self._invocation_history)

    def get_stats(self) -> Dict[str, ModelStats]:
        return dict(self._stats_by_policy)

    def get_total_stats(self) -> Dict[str, Any]:
        total_invocations = sum(s.total_invocations for s in self._stats_by_policy.values())
        total_tokens = sum(s.total_tokens for s in self._stats_by_policy.values())
        total_latency = sum(s.total_latency_ms for s in self._stats_by_policy.values())
        total_success = sum(s.success_count for s in self._stats_by_policy.values())
        total_failure = sum(s.failure_count for s in self._stats_by_policy.values())
        return {
            "total_invocations": total_invocations,
            "total_tokens": total_tokens,
            "total_latency_ms": total_latency,
            "total_success": total_success,
            "total_failure": total_failure,
            "avg_latency_ms": total_latency / max(total_invocations, 1),
            "policies": {p: s for p, s in self._stats_by_policy.items()},
        }


_model_provider: Optional[ModelProvider] = None


def get_model_provider() -> ModelProvider:
    global _model_provider
    if _model_provider is None:
        _model_provider = ModelProvider()
    return _model_provider


def initialize_models() -> ModelProvider:
    global _model_provider
    _model_provider = ModelProvider()
    _model_provider.initialize()
    return _model_provider


def get_model(policy: str) -> Optional[SmartFallbackModel]:
    """Get a model instance by policy name from the global provider."""
    provider = get_model_provider()
    return provider.get_model(policy)


def get_model_for_agent(agent_id: str) -> Optional[SmartFallbackModel]:
    """Get the recommended model for a specific agent from the global provider."""
    provider = get_model_provider()
    return provider.get_model_for_agent(agent_id)