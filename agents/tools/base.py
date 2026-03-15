"""Base tool contracts used by data source integrations."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class BaseToolResult:
    """Shared result shape for tool executions."""

    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
