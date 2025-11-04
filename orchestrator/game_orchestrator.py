"""
Game Orchestrator that coordinates player input, NPCs, and story progression.
Acts as the main interface for the player UI.
"""

import logging
from typing import Any
from datetime import datetime

from agents.llms import LLM_Model

from models import (
    NPCPersonality,
    GameSettings,
    ActionResponse,
    DialogueExchange,
    ActionType,
)
from agents.npc_agent import NPCAgent
from story.story_manager import StoryManager


class GameOrchestrator:
    """
    Main orchestrator that coordinates between player input, NPCs, and story management.
    This is the primary interface for the player UI.
    """

    def __init__(self, settings: GameSettings | None = None):
        """
        Initialize the game orchestrator.

        Args:
            settings: Game settings and configuration
        """
        self.settings: GameSettings = settings or GameSettings()
        self.story_manager: StoryManager = StoryManager(self.settings)
        self.npcs: dict[str, NPCAgent] = {}

        self.log("Game Orchestrator initialized")

    def log(self, message: str):
        """Log a message with orchestrator context"""
        logging.info(f"[GameOrchestrator] {message}")

    def set_settings(self, **kwargs):
        """Update game settings dynamically"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
                self.log(f"Updated setting: {key} = {value}")

    def add_npc(self, personality: NPCPersonality, model: LLM_Model | None):
        """
        Add an NPC to the game.

        Args:
            personality: The NPC's personality and background
            model: Optional LLM model override
        """
        agent = NPCAgent(personality, model or self.settings.llm_model)
        self.npcs[personality.name] = agent
        self.story_manager.register_npc_memory(personality.name, agent.memory)
        self.log(f"Added NPC: {personality.name}")

    def remove_npc(self, npc_name: str):
        """Remove an NPC from the game"""
        if npc_name in self.npcs:
            del self.npcs[npc_name]
            self.log(f"Removed NPC: {npc_name}")

    def get_npc(self, npc_name: str) -> NPCAgent | None:
        """Get an NPC agent by name"""
        return self.npcs.get(npc_name)

    def initialize_story(
        self,
        plot_points: list[str],
        active_goals: list[str],
        world_state: dict[str, Any],
    ):
        """
        Initialize the story with plot points, goals, and world state.

        Args:
            plot_points: Initial plot points
            active_goals: Active goals for the story
            world_state: Initial world state variables
        """
        self.story_manager.set_plot_points(plot_points)
        self.story_manager.set_active_goals(active_goals)
        for key, value in world_state.items():
            self.story_manager.update_world_state(key, value)

        self.log(
            f"Initialized story with {len(plot_points)} plot points and {len(active_goals)} goals"
        )

    def process_player_input(
        self, player_input: str, npc_name: str, player_id: str | None = None
    ) -> DialogueExchange:
        """
        Process player input and generate NPC response.
        This is the main interaction endpoint.

        Args:
            player_input: What the player said
            npc_name: Which NPC to interact with
            player_id: Optional player identifier

        Returns:
            DialogueExchange containing the NPC's response
        """
        self.log(f"Processing player input to {npc_name}: '{player_input[:50]}...'")

        # Get the NPC agent
        npc = self.get_npc(npc_name)
        if not npc:
            return DialogueExchange(
                player_input=player_input,
                npc_response=f"I don't know who {npc_name} is...",
                npc_name="System",
            )

        # Get current story state
        story_state = self.story_manager.story_state
        story_state.timestamp = datetime.now()

        # Generate NPC response
        action_response = npc.generate_dialogue(
            player_input, story_state, temperature=self.settings.temperature
        )

        # Record the conversation
        self.story_manager.record_conversation(
            player_input=player_input,
            npc_name=npc_name,
            npc_response=action_response.content,
            metadata=action_response.metadata,
        )

        # Update NPC memory in story manager
        self.story_manager.register_npc_memory(npc_name, npc.memory)

        # Create dialogue exchange
        exchange = DialogueExchange(
            player_input=player_input,
            npc_response=action_response.content,
            npc_name=npc_name,
            emotional_state=npc.personality.emotional_state,
        )

        self.log(f"Generated response from {npc_name}")

        return exchange

    def trigger_npc_action(
        self, npc_name: str, context: str, action_type: str = "interaction"
    ) -> ActionResponse:
        """
        Trigger an NPC to perform a non-dialogue action.

        Args:
            npc_name: Which NPC to trigger
            context: What's happening
            action_type: Type of action (dialogue, movement, emotion, etc.)

        Returns:
            ActionResponse describing what the NPC did
        """
        self.log(f"Triggering {action_type} action for {npc_name}")

        npc = self.get_npc(npc_name)
        if not npc:
            return ActionResponse(
                action_type=action_type,
                content=f"{npc_name} is not present.",
                npc_name="System",
            )

        story_state = self.story_manager.story_state
        story_state.timestamp = datetime.now()

        try:
            action_type_enum = ActionType[action_type.upper()]
        except KeyError:
            action_type_enum = ActionType.INTERACTION

        action_response = npc.generate_action(
            context,
            story_state,
            action_type=action_type_enum,
            temperature=self.settings.temperature,
        )

        self.log(f"{npc_name} performed action: {action_type}")

        return action_response

    def get_story_summary(self) -> str:
        """Get a summary of the current story state"""
        return self.story_manager.get_story_summary()

    def get_conversation_history(
        self, npc_name: str | None = None
    ) -> list[dict[str, str]]:
        """Get conversation history"""
        if npc_name:
            return [
                c
                for c in self.story_manager.conversation_history
                if c["npc_name"] == npc_name
            ]
        return self.story_manager.conversation_history

    def save_game(self, filepath: str):
        """Save the current game state"""
        self.story_manager.save_state(filepath)
        self.log(f"Game saved to {filepath}")

    def load_game(self, filepath: str):
        """Load a game state"""
        self.story_manager.load_state(filepath)
        self.log(f"Game loaded from {filepath}")

    def list_npcs(self) -> list[str]:
        """Get a list of all NPC names"""
        return list(self.npcs.keys())

    def get_npc_info(self, npc_name: str) -> dict[str, Any] | None:
        """Get information about an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return None

        return {
            "name": npc.personality.name,
            "backstory": npc.personality.backstory,
            "traits": npc.personality.personality_traits,
            "goals": npc.personality.goals,
            "emotional_state": npc.personality.emotional_state,
            "memory_summary": npc.get_memory_summary(),
        }
