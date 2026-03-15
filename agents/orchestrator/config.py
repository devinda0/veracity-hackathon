"""Configuration model for orchestrator behavior."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrchestratorConfig:
    """Configuration values for routing and synthesis behavior."""

    # Model selection
    router_model: str = "gemini-2.0-flash"
    agent_model: str = "gemini-2.0-flash"
    synthesis_model: str = "gemini-2.0-flash"

    # Execution behavior
    max_agents: int = 6
    max_iterations: int = 3
    timeout_seconds: int = 120

    # Observability
    enable_tracing: bool = True
    log_level: str = "INFO"

    # External dependencies
    gemini_api_key: Optional[str] = None
    mongo_uri: Optional[str] = None
    qdrant_url: Optional[str] = None
