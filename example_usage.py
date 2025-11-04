#!/usr/bin/env python3
"""
Example usage of the Dialogue Engine.

This demonstrates how to:
1. Set up the orchestrator with settings
2. Create NPCs with personalities
3. Initialize the story
4. Process player interactions
5. Trigger NPC actions

To run this example:
    cd /Users/matheusribeiro/Coding/Projetos/dialogue_engine
    python example_usage.py

Or if you encounter import issues:
    cd /Users/matheusribeiro/Coding/Projetos/dialogue_engine
    PYTHONPATH=. python example_usage.py
"""

import sys
import os
import logging
from pathlib import Path
from orchestrator.game_orchestrator import GameOrchestrator
from models import NPCPersonality, GameSettings

# Ensure the current directory is in the Python path
# This is needed for importing dialogue_engine modules
# current_dir = Path(__file__).parent.absolute()
# if str(current_dir) not in sys.path:
#     sys.path.insert(0, str(current_dir))

# Debug information
# print(f"Current working directory: {os.getcwd()}")
# print(f"Adding to Python path: {current_dir}")
# print(f"Python path includes current dir: {str(current_dir) in sys.path}")

# try:

#     print("✓ Successfully imported dialogue_engine modules")
# except ImportError as e:
#     print(f"✗ Failed to import dialogue_engine modules: {e}")
#     print("This typically happens when the package isn't properly recognized.")
#     print("Try running with: PYTHONPATH=. python example_usage.py")
#     sys.exit(1)

# Set up logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )


def main():
    """Main example demonstrating the dialogue engine"""

    print("=" * 60)
    print("Dialogue Engine Example")
    print("=" * 60)

    # 1. Initialize the orchestrator with settings
    from agents.llms import LLM_Model

    settings = GameSettings(
        llm_model=LLM_Model.DEEPSEEK_V3,
        temperature=0.8,
        max_tokens=500,
        story_style="adventure",
    )

    orchestrator = GameOrchestrator(settings)

    # 2. Create NPCs with personalities
    aragorn = NPCPersonality(
        name="Aragorn",
        backstory="A ranger from the North, heir to the throne of Gondor. Skilled in swordplay and tracking.",
        personality_traits=["noble", "protective", "determined", "wise"],
        goals=["Unite the kingdoms", "Protect the innocent", "Restore his line"],
        relationships={"Gandalf": "trusted ally", "Frodo": "sworn to protect"},
        speech_patterns="Speaks with gravitas and honor. Uses formal but warm language.",
        emotional_state="focused",
    )

    gandalf = NPCPersonality(
        name="Gandalf",
        backstory="A wise wizard of the Istari order. Ancient and powerful, but humble in appearance.",
        personality_traits=["wise", "patient", "powerful", "mysterious"],
        goals=["Guide the fellowship", "Oppose the darkness", "Preserve Middle-earth"],
        relationships={"Aragorn": "mentor and friend", "Frodo": "guide and protector"},
        speech_patterns="Speaks in riddles at times. Uses 'my dear' and 'indeed' frequently.",
        emotional_state="contemplative",
    )

    # Add NPCs to the orchestrator
    orchestrator.add_npc(aragorn, LLM_Model.GPT_OSS_OLLAMA)
    orchestrator.add_npc(gandalf, LLM_Model.GPT_OSS_OLLAMA)

    print("\n✓ NPCs created and added")

    # 3. Initialize the story
    orchestrator.initialize_story(
        plot_points=[
            "The One Ring has been found in the Shire",
            "A fellowship has been formed to destroy the ring",
            "They must pass through Moria",
            "Sauron's forces are searching for them",
        ],
        active_goals=[
            "Reach Mordor to destroy the ring",
            "Keep the ring-bearer safe",
            "Avoid detection by Sauron's forces",
        ],
        world_state={
            "location": "Moria",
            "time_of_day": "evening",
            "danger_level": "high",
            "party_size": 9,
        },
    )

    print("✓ Story initialized")

    # 4. Process player interactions
    print("\n" + "=" * 60)
    print("Starting Dialogue")
    print("=" * 60)

    # Simulate a conversation with Aragorn
    print("\n[Player]", "We're being followed! What should we do?")
    response1 = orchestrator.process_player_input(
        "We're being followed! What should we do?", "Aragorn"
    )
    print(f"[{response1.npc_name}]", response1.npc_response)

    print("\n[Player]", "But Gandalf said we should avoid fighting if possible.")
    response2 = orchestrator.process_player_input(
        "But Gandalf said we should avoid fighting if possible.", "Aragorn"
    )
    print(f"[{response2.npc_name}]", response2.npc_response)

    # Talk to Gandalf
    print("\n[Player]", "Gandalf, what do you think we should do?")
    response3 = orchestrator.process_player_input(
        "Gandalf, what do you think we should do?", "Gandalf"
    )
    print(f"[{response3.npc_name}]", response3.npc_response)

    # 5. Trigger an NPC action
    print("\n" + "=" * 60)
    print("Triggering NPC Actions")
    print("=" * 60)

    print("\n[A narrator]", "As the party approaches a dark passage...")
    action1 = orchestrator.trigger_npc_action(
        "Aragorn",
        "The party needs someone to scout ahead in the dark passage",
        "interaction",
    )
    print(f"[{action1.npc_name}]", action1.content)

    print("\n[A narrator]", "A mysterious light appears...")
    action2 = orchestrator.trigger_npc_action(
        "Gandalf", "A mysterious glow appears in Gandalf's staff", "interaction"
    )
    print(f"[{action2.npc_name}]", action2.content)

    # 6. View story summary
    print("\n" + "=" * 60)
    print("Story Summary")
    print("=" * 60)
    print(orchestrator.get_story_summary())

    # 7. List all NPCs
    print("\n" + "=" * 60)
    print("Available NPCs")
    print("=" * 60)
    for npc_name in orchestrator.list_npcs():
        info = orchestrator.get_npc_info(npc_name)
        if info:
            print(f"\n{info['name']}:")
            print(f"  Traits: {', '.join(info['traits'])}")
            print(f"  State: {info['emotional_state']}")
            print(f"  Memory: {info['memory_summary']}")

    # 8. Save the game
    print("\n" + "=" * 60)
    print("Saving Game")
    print("=" * 60)
    orchestrator.save_game("example_game_state.json")
    print("✓ Game saved to example_game_state.json")

    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
