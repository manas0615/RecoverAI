import logging
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError

from recoverai.intelligence.gateway import GatewayError
from recoverai.state_machine.exceptions import (
    InvalidTransitionError,
    TerminalStateError,
    UnknownStateError,
)

logger = logging.getLogger(__name__)


class MCPError(Exception):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


class MCPToolRegistry:
    def __init__(self, context: Any):
        self.context = context
        self.tools: dict[str, dict] = {}
        self.handlers: dict[str, tuple[type[BaseModel], Callable]] = {}

    def register(
        self,
        name: str,
        category: str,
        risk: str,
        schema: type[BaseModel],
        handler: Callable,
        requires_policy: bool = False,
        requires_verification: bool = False,
        idempotency_required: bool = False,
    ) -> None:
        self.tools[name] = {
            "name": name,
            "category": category,
            "risk": risk,
            "inputSchema": schema.model_json_schema(),
            "requires_policy": requires_policy,
            "requires_verification": requires_verification,
            "idempotency_required": idempotency_required,
        }
        self.handlers[name] = (schema, handler)

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name not in self.handlers:
            return {"error": f"Unknown tool: {tool_name}", "code": "UNKNOWN_TOOL"}

        schema_cls, handler = self.handlers[tool_name]
        try:
            validated_args = schema_cls.model_validate(arguments)
        except ValidationError as e:
            return {
                "error": "Invalid input arguments",
                "code": "INVALID_INPUT",
                "details": e.errors(),
            }

        try:
            result = handler(self.context, validated_args)
            return {"success": True, "data": result}
        except (InvalidTransitionError, TerminalStateError, UnknownStateError) as e:
            return {"error": str(e), "code": "INVALID_WORKFLOW_STATE"}
        except MCPError as e:
            logger.warning(f"Tool {tool_name} failed with business error: {e}")
            return {"error": str(e), "code": e.code}
        except ValueError as e:
            # Often used for Not Found in repositories
            if "not found" in str(e).lower():
                return {"error": str(e), "code": "NOT_FOUND"}
            return {"error": str(e), "code": "INVALID_INPUT"}
        except GatewayError as e:
            logger.warning(f"Tool {tool_name} failed with LLM Gateway error: {e}")
            return {"error": "AI Provider Failure", "code": "PROVIDER_FAILURE"}
        except Exception as e:  # noqa: BLE001
            logger.error(f"Tool {tool_name} internal failure: {e}")
            return {"error": "Internal execution failure", "code": "INTERNAL_ERROR"}
