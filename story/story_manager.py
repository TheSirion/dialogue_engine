"""
Story Manager that tracks plot state, memory, and goal management.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from models import StoryState, NPCMemory, GameSettings


class StoryManager:
    """
    Manages story state, plot progression, memory, and goals.
    Acts as the central coordinator for story elements.
    """

    def __init__(self, settings: Optional[GameSettings] = None):
        """
        Initialize the Story Manager.

        Args:
            settings: Game settings and configuration
        """
        self.settings = settings or GameSettings()
        self.story_state = StoryState()
        self.npc_memories: Dict[str, NPCMemory] = {}
        self.conversation_history: List[Dict[str, Any]] = []

        self.log("Story Manager initialized")

    def log(self, message: str):
        """Log a message with story manager context"""
        logging.info(f"[StoryManager] {message}")

    def set_plot_points(self, plot_points: List[str]):
        """
        Set or update plot points in the story.

        Args:
            plot_points: List of plot point descriptions
        """
        self.story_state.plot_points = plot_points
        self.log(f"Set {len(plot_points)} plot points")

    def add_plot_point(self, plot_point: str):
        """Add a single plot point to the story"""
        self.story_state.plot_points.append(plot_point)
        self.log(f"Added plot point: {plot_point[:50]}...")

    def complete_event(self, event_name: str):
        """
        Mark an event as completed.

        Args:
            event_name: Name/description of the completed event
        """
        if event_name not in self.story_state.completed_events:
            self.story_state.completed_events.append(event_name)
            self.log(f"Completed event: {event_name}")

    def set_active_goals(self, goals: List[str]):
        """
        Set active goals for the story.

        Args:
            goals: List of goal descriptions
        """
        self.story_state.active_goals = goals
        self.log(f"Set {len(goals)} active goals")

    def add_active_goal(self, goal: str):
        """Add an active goal"""
        if goal not in self.story_state.active_goals:
            self.story_state.active_goals.append(goal)
            self.log(f"Added active goal: {goal}")

    def complete_goal(self, goal: str):
        """Mark a goal as completed"""
        if goal in self.story_state.active_goals:
            self.story_state.active_goals.remove(goal)
            self.log(f"Completed goal: {goal}")

    def update_world_state(self, key: str, value: Any):
        """
        Update a world state variable.

        Args:
            key: The world state key
            value: The value to set
        """
        self.story_state.world_state[key] = value
        self.log(f"Updated world state: {key} = {value}")

    def get_world_state(self, key: str, default: Any = None) -> Any:
        """Get a world state variable"""
        return self.story_state.world_state.get(key, default)

    def record_conversation(
        self,
        player_input: str,
        npc_name: str,
        npc_response: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Record a conversation exchange.

        Args:
            player_input: What the player said
            npc_name: Name of the NPC
            npc_response: What the NPC said
            metadata: Additional metadata about the exchange
        """
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "player_input": player_input,
            "npc_name": npc_name,
            "npc_response": npc_response,
            "metadata": metadata or {},
        }
        self.conversation_history.append(exchange)

        # Keep last 100 conversations to prevent memory bloat
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]

    def get_conversation_summary(
        self, npc_name: Optional[str] = None, last_n: int = 5
    ) -> str:
        """
        Get a summary of recent conversations.

        Args:
            npc_name: Filter by specific NPC (None for all)
            last_n: Number of recent conversations to include

        Returns:
            Summary string
        """
        conversations = self.conversation_history
        if npc_name:
            conversations = [c for c in conversations if c["npc_name"] == npc_name]

        conversations = conversations[-last_n:]

        if not conversations:
            return "No recent conversations."

        summary = "Recent conversations:\n"
        for conv in conversations:
            summary += f"\n- Player: {conv['player_input'][:50]}...\n"
            summary += f"  {conv['npc_name']}: {conv['npc_response'][:50]}...\n"

        return summary

    def get_story_summary(self) -> str:
        """
        Get a summary of the current story state.

        Returns:
            Formatted story summary
        """
        summary = f"# Story Summary\n\n"
        summary += f"## Plot Points ({len(self.story_state.plot_points)}):\n"
        for i, point in enumerate(self.story_state.plot_points, 1):
            summary += f"{i}. {point}\n"

        summary += f"\n## Active Goals ({len(self.story_state.active_goals)}):\n"
        for i, goal in enumerate(self.story_state.active_goals, 1):
            summary += f"{i}. {goal}\n"

        summary += (
            f"\n## Completed Events ({len(self.story_state.completed_events)}):\n"
        )
        for i, event in enumerate(self.story_state.completed_events, 1):
            summary += f"{i}. {event}\n"

        summary += (
            f"\n## World State:\n{json.dumps(self.story_state.world_state, indent=2)}\n"
        )

        return summary

    def save_state(self, filepath: str):
        """
        Save the story state to a file.

        Args:
            filepath: Path to save the state
        """
        # dict representation
        settings_dict = self.settings.model_dump()

        # Convert LLM_Model enum to its string value for JSON serialization
        if "llm_model" in settings_dict and settings_dict["llm_model"] is not None:
            from enum import Enum

            if isinstance(settings_dict["llm_model"], Enum):
                settings_dict["llm_model"] = settings_dict["llm_model"].value

        # Handle datetime serialization
        import json
        from datetime import datetime

        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        story_state_dict = self.story_state.model_dump()
        npc_memories_dict = {k: v.model_dump() for k, v in self.npc_memories.items()}

        data = {
            "story_state": story_state_dict,
            "npc_memories": npc_memories_dict,
            "conversation_history": self.conversation_history,
            "settings": settings_dict,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=json_serializer)

        self.log(f"Saved story state to {filepath}")

    def load_state(self, filepath: str):
        """
        Load the story state from a file.

        Args:
            filepath: Path to load the state from
        """
        if not os.path.exists(filepath):
            self.log(f"State file not found: {filepath}")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        self.story_state = StoryState(**data.get("story_state", {}))
        self.npc_memories = {
            k: NPCMemory(**v) for k, v in data.get("npc_memories", {}).items()
        }
        self.conversation_history = data.get("conversation_history", [])

        if "settings" in data:
            settings_data = data["settings"].copy()
            # Convert string value back to Enum when loading
            if "llm_model" in settings_data and isinstance(
                settings_data["llm_model"], str
            ):
                from ..agents.llms import LLM_Model

                # Find the enum value that matches the string
                for model in LLM_Model:
                    if model.value == settings_data["llm_model"]:
                        settings_data["llm_model"] = model
                        break
            self.settings = GameSettings(**settings_data)

        self.log(f"Loaded story state from {filepath}")

    def register_npc_memory(self, npc_name: str, memory: NPCMemory):
        """Register an NPC's memory with the story manager"""
        self.npc_memories[npc_name] = memory
        self.log(f"Registered memory for {npc_name}")

    def get_npc_memory(self, npc_name: str) -> Optional[NPCMemory]:
        """Get an NPC's memory"""
        return self.npc_memories.get(npc_name)
