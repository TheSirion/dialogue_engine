"""
Demo showing how to integrate the dialogue engine with external systems.
This demonstrates the two main endpoints: Player UI and Story Management.
"""

import logging
from typing import Dict, Any
from orchestrator import GameOrchestrator
from models import NPCPersonality, GameSettings


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class PlayerUIInterface:
    """
    Demo interface simulating a player UI connection.
    This would be replaced by your actual UI (web, desktop, etc.)
    """

    def __init__(self):
        """Initialize the player UI interface"""
        self.orchestrator = None
        self.current_player_id = None

    def connect(self, orchestrator: GameOrchestrator):
        """Connect to the game orchestrator"""
        self.orchestrator = orchestrator
        print("✓ Player UI connected to orchestrator")

    def send_player_input(self, text: str, npc_name: str) -> Dict[str, Any]:
        """
        Send player input and get NPC response.
        This is the main interaction endpoint for the UI.

        Returns:
            Dictionary with response data for UI rendering
        """
        if not self.orchestrator:
            raise RuntimeError("Not connected to orchestrator")

        exchange = self.orchestrator.process_player_input(text, npc_name)

        return {
            "response": exchange.npc_response,
            "npc": exchange.npc_name,
            "emotional_state": exchange.emotional_state,
            "timestamp": exchange.timestamp.isoformat(),
        }

    def get_available_npcs(self) -> list:
        """Get list of NPCs the player can interact with"""
        if not self.orchestrator:
            return []
        return self.orchestrator.list_npcs()

    def get_npc_info(self, npc_name: str) -> Dict[str, Any]:
        """Get information about a specific NPC"""
        if not self.orchestrator:
            return {}
        return self.orchestrator.get_npc_info(npc_name) or {}


class StorySystemInterface:
    """
    Demo interface for the story system connection.
    This manages plot, memory, and goals separately from player interactions.
    """

    def __init__(self):
        """Initialize the story system interface"""
        self.orchestrator = None

    def connect(self, orchestrator: GameOrchestrator):
        """Connect to the game orchestrator"""
        self.orchestrator = orchestrator
        print("✓ Story System connected to orchestrator")

    def get_story_state(self) -> Dict[str, Any]:
        """Get current story state"""
        if not self.orchestrator:
            return {}

        story_manager = self.orchestrator.story_manager
        return {
            "plot_points": story_manager.story_state.plot_points,
            "active_goals": story_manager.story_state.active_goals,
            "completed_events": story_manager.story_state.completed_events,
            "world_state": story_manager.story_state.world_state,
        }

    def update_plot(self, plot_point: str):
        """Add a new plot point"""
        if not self.orchestrator:
            return
        self.orchestrator.story_manager.add_plot_point(plot_point)

    def complete_goal(self, goal: str):
        """Mark a goal as completed"""
        if not self.orchestrator:
            return
        self.orchestrator.story_manager.complete_goal(goal)

    def update_world_state(self, key: str, value: Any):
        """Update a world state variable"""
        if not self.orchestrator:
            return
        self.orchestrator.story_manager.update_world_state(key, value)

    def save_game(self, filepath: str):
        """Save the current game state"""
        if not self.orchestrator:
            return
        self.orchestrator.save_game(filepath)

    def load_game(self, filepath: str):
        """Load a saved game state"""
        if not self.orchestrator:
            return
        self.orchestrator.load_game(filepath)


def main():
    """
    Demo showing how the two interfaces work together.
    """
    print("=" * 70)
    print("Dialogue Engine Integration Demo")
    print("Demonstrating Player UI Orchestrator and Story System Endpoints")
    print("=" * 70)

    # 1. Setup game
    settings = GameSettings(
        llm_model="gpt-4o-mini", temperature=0.7, story_style="adventure"
    )

    orchestrator = GameOrchestrator(settings)

    # 2. Initialize story
    orchestrator.initialize_story(
        plot_points=[
            "The player arrives in the ancient city of Eldoria",
            "A mysterious artifact has been stolen",
            "The city guards are suspicious of all newcomers",
        ],
        active_goals=["Clear your name", "Find the artifact", "Discover who stole it"],
        world_state={
            "location": "market_square",
            "time": "morning",
            "weather": "clear",
            "suspicion_level": "high",
        },
    )

    # 3. Create NPCs
    guard = NPCPersonality(
        name="Captain Aldric",
        backstory="A veteran city guard, suspicious of strangers. Has seen too many crimes.",
        personality_traits=["suspicious", "duty-bound", "gruff"],
        goals=["Protect the city", "Find the artifact thief"],
        relationships={"The Player": "suspicious stranger"},
        speech_patterns="Speaks formally and with authority. Uses 'citizen' to address people.",
        emotional_state="alert",
    )

    merchant = NPCPersonality(
        name="Merchant Esme",
        backstory="A friendly merchant who loves gossip. Knows everyone's business.",
        personality_traits=["talkative", "friendly", "curious"],
        goals=["Sell her wares", "Spread news", "Help customers"],
        relationships={"Captain Aldric": "customer and informant"},
        speech_patterns="Very talkative, uses 'darling' and 'honey'. Tends to ramble with excitement.",
        emotional_state="cheerful",
    )

    orchestrator.add_npc(guard)
    orchestrator.add_npc(merchant)

    print("\n✓ Game setup complete\n")

    # 4. Initialize interfaces
    player_ui = PlayerUIInterface()
    story_system = StorySystemInterface()

    player_ui.connect(orchestrator)
    story_system.connect(orchestrator)

    # 5. Demonstrate Player UI endpoint usage
    print("\n" + "=" * 70)
    print("PLAYER UI INTERACTIONS")
    print("=" * 70)

    print("\n[Available NPCs]:", ", ".join(player_ui.get_available_npcs()))

    print("\n[Player]", "Hello, I'm new in town. What's going on?")
    response1 = player_ui.send_player_input(
        "Hello, I'm new in town. What's going on?", "Merchant Esme"
    )
    print(f"[{response1['npc']}]", response1["response"])
    print(f"  Emotional state: {response1['emotional_state']}")

    print("\n[Player]", "Captain, I need to speak with you about the stolen artifact.")
    response2 = player_ui.send_player_input(
        "Captain, I need to speak with you about the stolen artifact.", "Captain Aldric"
    )
    print(f"[{response2['npc']}]", response2["response"])
    print(f"  Emotional state: {response2['emotional_state']}")

    # Get NPC info
    print("\n[Player UI] Querying NPC info...")
    guard_info = player_ui.get_npc_info("Captain Aldric")
    print(f"  Name: {guard_info['name']}")
    print(f"  Traits: {', '.join(guard_info['traits'])}")
    print(f"  State: {guard_info['emotional_state']}")

    # 6. Demonstrate Story System endpoint usage
    print("\n" + "=" * 70)
    print("STORY SYSTEM MANAGEMENT")
    print("=" * 70)

    # Get current state
    print("\n[Story System] Getting current story state...")
    state = story_system.get_story_state()
    print(f"  Plot points: {len(state['plot_points'])}")
    print(f"  Active goals: {len(state['active_goals'])}")
    print(f"  World state keys: {list(state['world_state'].keys())}")

    # Update plot
    print("\n[Story System] Adding new plot point...")
    story_system.update_plot("The player finds a clue: a dropped badge")

    # Update world state
    print("\n[Story System] Updating world state...")
    story_system.update_world_state("player_found_clue", True)
    story_system.update_world_state("suspicion_level", "medium")

    # Complete a goal
    print("\n[Story System] Completing goal...")
    story_system.complete_goal("Clear your name")

    # Check updated state
    print("\n[Story System] Updated story state:")
    state = story_system.get_story_state()
    print(f"  Plot points: {len(state['plot_points'])}")
    print(f"  Active goals: {len(state['active_goals'])}")
    print(f"  Suspicion level: {state['world_state'].get('suspicion_level')}")
    print(f"  Clue found: {state['world_state'].get('player_found_clue')}")

    # 7. Demonstrate save/load
    print("\n" + "=" * 70)
    print("GAME STATE MANAGEMENT")
    print("=" * 70)

    print("\n[Story System] Saving game...")
    story_system.save_game("demo_game_state.json")

    print("\n[Story System] Story summary:")
    summary = orchestrator.get_story_summary()
    print(summary)

    print("\n" + "=" * 70)
    print("Integration Demo Complete!")
    print("=" * 70)
    print("\nThe game state has been saved to 'demo_game_state.json'")
    print("You can load it later using:")
    print("  story_system.load_game('demo_game_state.json')")


if __name__ == "__main__":
    main()
