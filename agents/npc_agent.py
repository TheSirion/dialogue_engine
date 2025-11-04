"""
NPC Agent that uses LLMs to generate dialogue and actions.
"""

import os
import json
import logging

from models import (
    NPCPersonality,
    StoryState,
    NPCMemory,
    ActionResponse,
    ActionType,
)
from .llms import Text_Generator, LLM_Model


class NPCAgent:
    """
    An agent that represents an NPC, capable of generating dialogue and actions
    based on personality, story context, and memory.
    """

    def __init__(self, personality: NPCPersonality, model: LLM_Model):
        """
        Initialize an NPC agent.

        Args:
            personality: The NPC's personality traits and background
            model: The LLM model to use for generation
        """
        self.personality: NPCPersonality = personality
        self.model: LLM_Model = model
        self.memory: NPCMemory = NPCMemory(npc_name=personality.name)
        self.llm: Text_Generator = Text_Generator(model)

        # Initialize OpenAI client
        # deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        # if deepseek_api_key:
        #     self.client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
        #     self.model = "deepseek-chat"
        #     self.log("NPCAgent set up with DeepSeek")
        # else:
        #     self.client = OpenAI()
        #     self.log("NPCAgent set up with OpenAI")
        logging.info(f"NPC agent set up with {model.value}")

        logging.info(
            f"[{personality.name}] Initialized NPCAgent with model: {self.model}"
        )

    def log(self, message: str):
        """Log a message with agent context"""
        logging.info(f"[{self.personality.name}] {message}")

    def _build_context_prompt(self, player_input: str, story_state: StoryState) -> str:
        """
        Build a comprehensive context prompt for the LLM.

        Args:
            player_input: What the player just said
            story_state: Current state of the story

        Returns:
            Formatted context string
        """
        prompt = f"""You are {self.personality.name}, a character in an interactive story.

        ## Your Background:
        {self.personality.backstory}

        ## Your Personality Traits:
        {", ".join(self.personality.personality_traits)}

        ## Your Current Emotional State:
        {self.personality.emotional_state}

        ## Your Goals:
        {chr(10).join(f"- {goal}" for goal in self.personality.goals)}

        ## Story Context:
        ### Plot Points:
        {chr(10).join(f"- {point}" for point in story_state.plot_points)}

        ### Active Goals:
        {chr(10).join(f"- {goal}" for goal in story_state.active_goals)}

        ### World State:
        {json.dumps(story_state.world_state, indent=2)}

        ## Your Recent Memories:
        """
        if self.memory.memories:
            for mem in self.memory.memories[-5:]:  # Last 5 memories
                prompt += f"- {mem.get('description', mem)}\n"
        else:
            prompt += "- No specific memories yet.\n"

        if self.personality.speech_patterns:
            prompt += (
                f"\n## Your Speech Patterns:\n{self.personality.speech_patterns}\n"
            )

        prompt += f"""
        ## The Player Says:
        "{player_input}"

        ## Your Task:
        Respond naturally as {self.personality.name}. Consider your personality, goals, emotional state, and the story context.
        Your response should be authentic, consistent with your character, and advance the story naturally.

        Respond with ONLY your dialogue, keeping it concise (2-3 sentences max)."""

        return prompt

    def generate_dialogue(
        self,
        player_input: str,
        story_state: StoryState,
        temperature: float = 0.8,
        max_tokens: int = 100,
    ) -> ActionResponse:
        """
        Generate a dialogue response based on player input and story context.

        Args:
            player_input: What the player said
            story_state: Current story state
            temperature: LLM temperature for creativity

        Returns:
            ActionResponse containing the dialogue
        """
        self.log(f"Generating dialogue for player input: '{player_input[:50]}...'")

        context_prompt = self._build_context_prompt(player_input, story_state)

        try:
            response = self.llm.generate_text(
                [
                    {
                        "role": "system",
                        "content": "You are an expert at role-playing and creating immersive dialogue for interactive stories.",
                    },
                    {"role": "user", "content": context_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            dialogue_text: str | None = response if response else "..."

            # Remove quotes if the LLM adds them
            if (dialogue_text.startswith('"') and dialogue_text.endswith('"')) or (
                dialogue_text.startswith("'") and dialogue_text.endswith("'")
            ):
                dialogue_text = dialogue_text[1:-1]

            self.log(f"Generated dialogue: '{dialogue_text[:50]}...'")

            # Store in memory
            self.memory.memories.append(
                {
                    "type": "dialogue",
                    "player_input": player_input,
                    "npc_response": dialogue_text,
                    "timestamp": story_state.timestamp.isoformat(),
                }
            )
            self.memory.player_interactions += 1

            return ActionResponse(
                action_type=ActionType.DIALOGUE,
                content=dialogue_text,
                npc_name=self.personality.name,
                metadata={
                    "emotional_state": self.personality.emotional_state,
                    "model": self.model,
                },
            )

        except Exception as e:
            self.log(f"Error generating dialogue: {e}")
            return ActionResponse(
                action_type=ActionType.DIALOGUE,
                content="...I need a moment to collect my thoughts.",
                npc_name=self.personality.name,
                metadata={"error": str(e)},
            )

    def generate_action(
        self,
        context: str,
        story_state: StoryState,
        action_type: ActionType = ActionType.INTERACTION,
        temperature: float = 0.8,
    ) -> ActionResponse:
        """
        Generate a non-dialogue action based on context.

        Args:
            context: What's happening in the scene
            story_state: Current story state
            action_type: Type of action to generate
            temperature: LLM temperature

        Returns:
            ActionResponse containing the action description
        """
        self.log(f"Generating {action_type.value} action")

        prompt = f"""You are {self.personality.name}, a character in an interactive story.

        ## Your Background:
        {self.personality.backstory}

        ## Your Personality Traits:
        {", ".join(self.personality.personality_traits)}

        ## Your Current Emotional State:
        {self.personality.emotional_state}

        ## Current Context:
        {context}

        ## Story State:
        {json.dumps(story_state.world_state, indent=2)}

        ## Your Task:
        Describe what {self.personality.name} does in this situation. Be creative and true to your character.
        Keep it brief (1-2 sentences)."""

        try:
            response = self.llm.generate_text(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at role-playing and creating immersive actions for interactive stories.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=300,
            )

            action_text = response.strip()

            # Store in memory
            self.memory.memories.append(
                {
                    "type": action_type.value,
                    "context": context,
                    "action": action_text,
                    "timestamp": story_state.timestamp.isoformat(),
                }
            )

            return ActionResponse(
                action_type=action_type,
                content=action_text,
                npc_name=self.personality.name,
                metadata={"model": self.model},
            )

        except Exception as e:
            self.log(f"Error generating action: {e}")
            return ActionResponse(
                action_type=action_type,
                content=f"{self.personality.name} stands quietly.",
                npc_name=self.personality.name,
                metadata={"error": str(e)},
            )

    def get_memory_summary(self) -> str:
        """Get a summary of the NPC's memories"""
        return f"{self.personality.name} has {len(self.memory.memories)} memories and {self.memory.player_interactions} interactions with the player."

    def update_personality(self, **kwargs):
        """
        Update personality attributes dynamically.

        Args:
            **kwargs: Personality attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self.personality, key):
                setattr(self.personality, key, value)
                self.log(f"Updated {key} to {value}")
