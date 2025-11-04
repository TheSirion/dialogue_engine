"""
Data models for the dialogue engine system.
"""

from pydantic import BaseModel, Field
from typing import Any, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .agents.llms import LLM_Model
else:
    # Defer import to avoid circular dependency
    LLM_Model = None


class ActionType(str, Enum):
    """Types of actions an NPC can take"""

    DIALOGUE = "dialogue"
    MOVEMENT = "movement"
    EMOTION = "emotion"
    INTERACTION = "interaction"
    STORY_EVENT = "story_event"


class NPCPersonality(BaseModel):
    """Defines the personality traits of an NPC"""

    name: str
    backstory: str
    personality_traits: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(
        default_factory=dict
    )  # NPC name -> relationship description
    speech_patterns: str | None = None
    emotional_state: str = "neutral"


class StoryState(BaseModel):
    """Current state of the story"""

    plot_points: list[str] = Field(default_factory=list)
    completed_events: list[str] = Field(default_factory=list)
    active_goals: list[str] = Field(default_factory=list)
    world_state: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class NPCMemory(BaseModel):
    """NPC's memory of past interactions"""

    npc_name: str
    memories: list[dict[str, Any]] = Field(default_factory=list)
    important_events: list[str] = Field(default_factory=list)
    player_interactions: int = 0


class PlayerInput(BaseModel):
    """Input from the player"""

    text: str
    player_id: str
    context: dict[str, Any] | None = None


class ActionResponse(BaseModel):
    """Response from an NPC action"""

    action_type: ActionType
    content: str
    npc_name: str
    metadata: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class DialogueExchange(BaseModel):
    """A single exchange in a dialogue"""

    player_input: str | None = None
    npc_response: str
    npc_name: str
    emotional_state: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class GameSettings(BaseModel):
    """Overall game settings"""

    llm_model: str | None = None
    temperature: float = 0.8
    max_tokens: int = 500
    story_style: str = "adventure"  # adventure, mystery, romance, etc.
    difficulty: str = "medium"
    custom_instructions: str | None = None

    # def __init__(self, **data):
    # Import here to avoid circular dependency
    # if "llm_model" not in data or data.get("llm_model") is None:
    #     from .agents.llms import LLM_Model

    #     data["llm_model"] = LLM_Model.GPT_OSS_OLLAMA
    # super().__init__(**data)
