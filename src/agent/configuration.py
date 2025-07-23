"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import ensure_config
from langgraph.config import get_config
from langchain_core.runnables import RunnableConfig

from agent.prompts import SYSTEM_PROMPT


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    user_id: str = field(
        default="walt-boxwell",
        metadata={"description": "The ID of the user."},
    )

    user_name: str = field(
        default="Walt Boxwell",
        metadata={"description": "The name of the user."},
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        # default="groq:llama-3.3-70b-versatile",
        # default="openai:gpt-4o-mini",
        default="openai:gpt-4.1",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider:model-name."
        },
    )

    api_key: str = field(
        default="",
        metadata={
            "description": "The API key to use for the agent's main interactions. "
        },
    )

    system_prompt: str = field(
        default=SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        try:
            config = get_config()
        except RuntimeError:
            config = None
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
