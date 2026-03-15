"""Base tool contracts used by data source integrations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from agents.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorType(str, Enum):
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


@dataclass
class ToolResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    attempts: int = 0
    duration_ms: float = 0.0


class CircuitBreaker:
    """Circuit breaker for failing services."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("circuit_breaker_opened")

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        if not self.is_open:
            return True

        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed > self.recovery_timeout:
                self.is_open = False
                self.failure_count = 0
                logger.info("circuit_breaker_recovered")
                return True

        return False


class BaseDataSourceTool(ABC):
    """Base class for data source tools."""

    def __init__(
        self,
        name: str,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        rate_limit: int = 5,
    ):
        self.name = name
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.rate_limiter = asyncio.Semaphore(rate_limit)
        self.circuit_breaker = CircuitBreaker()

    async def execute(self, **kwargs) -> ToolResult:
        """Main execution method with retry + rate limiting."""

        if not self.circuit_breaker.can_execute():
            return ToolResult(
                success=False,
                error="Service temporarily unavailable (circuit breaker open)",
                error_type=ErrorType.UNKNOWN,
            )

        start_time = time.time()
        attempt = 0
        error_type = ErrorType.UNKNOWN

        while attempt < self.max_retries:
            attempt += 1

            try:
                async with self.rate_limiter:
                    result = await asyncio.wait_for(
                        self._fetch(**kwargs),
                        timeout=self.timeout_seconds,
                    )

                self.circuit_breaker.record_success()

                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "tool_execution_success",
                    tool=self.name,
                    attempt=attempt,
                    duration_ms=duration_ms,
                )

                return ToolResult(
                    success=True,
                    data=result,
                    attempts=attempt,
                    duration_ms=duration_ms,
                )

            except asyncio.TimeoutError:
                error_type = ErrorType.TIMEOUT
                logger.warning(
                    "tool_execution_timeout",
                    tool=self.name,
                    attempt=attempt,
                )

            except Exception as e:
                error_msg = str(e)

                if "rate limit" in error_msg.lower():
                    error_type = ErrorType.RATE_LIMIT
                    await asyncio.sleep(2 ** attempt)
                elif "connection" in error_msg.lower():
                    error_type = ErrorType.NETWORK
                else:
                    error_type = ErrorType.UNKNOWN

                logger.warning(
                    "tool_execution_failed",
                    tool=self.name,
                    attempt=attempt,
                    error_type=error_type,
                    error=error_msg,
                )

            if attempt < self.max_retries:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** (attempt - 1)
                await asyncio.sleep(wait_time)

        # All retries exhausted
        self.circuit_breaker.record_failure()

        duration_ms = (time.time() - start_time) * 1000
        return ToolResult(
            success=False,
            error=f"Failed after {attempt} attempts",
            error_type=error_type,
            attempts=attempt,
            duration_ms=duration_ms,
        )

    @abstractmethod
    async def _fetch(self, **kwargs) -> Dict[str, Any]:
        """
        Subclasses implement this method to fetch data.
        Should raise exceptions for errors.
        """
        pass

    def reset_circuit_breaker(self):
        """Manual circuit breaker reset."""
        self.circuit_breaker = CircuitBreaker()
        logger.info("circuit_breaker_reset", tool=self.name)
