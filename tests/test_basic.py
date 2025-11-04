"""
Basic tests for the dialogue engine.
"""

import pytest
from dialogue_engine.models import NPCPersonality, GameSettings, ActionType
from dialogue_engine.orchestrator import GameOrchestrator
from dialogue_engine.agents import NPCAgent


def test_npc_personality_creation():
    """Test creating an NPC personality"""
    npc = NPCPersonality(
        name="Test NPC",
        backstory="A test character",
        personality_traits=["friendly", "helpful"],
        goals=["Help the player"]
    )
    
    assert npc.name == "Test NPC"
    assert npc.backstory == "A test character"
    assert len(npc.personality_traits) == 2
    assert npc.emotional_state == "neutral"


def test_settings_creation():
    """Test creating game settings"""
    settings = GameSettings(
        llm_model="gpt-4o-mini",
        temperature=0.8
    )
    
    assert settings.llm_model == "gpt-4o-mini"
    assert settings.temperature == 0.8


def test_orchestrator_initialization():
    """Test initializing the game orchestrator"""
    settings = GameSettings()
    orchestrator = GameOrchestrator(settings)
    
    assert orchestrator.settings is not None
    assert len(orchestrator.npcs) == 0


def test_add_npc():
    """Test adding an NPC to the orchestrator"""
    settings = GameSettings()
    orchestrator = GameOrchestrator(settings)
    
    npc = NPCPersonality(
        name="Guard",
        backstory="A town guard",
        personality_traits=["alert", "serious"]
    )
    
    orchestrator.add_npc(npc)
    
    assert "Guard" in orchestrator.npcs
    assert len(orchestrator.npcs) == 1


def test_story_initialization():
    """Test initializing story state"""
    settings = GameSettings()
    orchestrator = GameOrchestrator(settings)
    
    orchestrator.initialize_story(
        plot_points=["Test point 1", "Test point 2"],
        active_goals=["Goal 1"],
        world_state={"test": "value"}
    )
    
    assert len(orchestrator.story_manager.story_state.plot_points) == 2
    assert len(orchestrator.story_manager.story_state.active_goals) == 1
    assert orchestrator.story_manager.get_world_state("test") == "value"


def test_action_types():
    """Test action type enum"""
    assert ActionType.DIALOGUE == "dialogue"
    assert ActionType.MOVEMENT == "movement"
    assert ActionType.EMOTION == "emotion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

