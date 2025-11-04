# Quick Reference Card

## Installation

```bash
pip install openai python-dotenv pydantic
```

```bash
# .env file
OPENAI_API_KEY=your_key_here
```

## Basic Usage

```python
from dialogue_engine.orchestrator import GameOrchestrator
from dialogue_engine.models import NPCPersonality, GameSettings

# 1. Setup
settings = GameSettings(llm_model="gpt-4o-mini", temperature=0.8)
game = GameOrchestrator(settings)

# 2. Create NPC
npc = NPCPersonality(
    name="Merchant",
    backstory="A traveling merchant",
    personality_traits=["friendly", "greedy"],
    goals=["Sell wares"]
)
game.add_npc(npc)

# 3. Initialize story
game.initialize_story(
    plot_points=["Find the artifact"],
    active_goals=["Quest to save the world"],
    world_state={"location": "town"}
)

# 4. Talk to NPC
response = game.process_player_input("Hello!", "Merchant")
print(response.npc_response)
```

## Common Patterns

### Player UI Endpoint

```python
# Send player input
exchange = orchestrator.process_player_input(text, npc_name)
# Returns: DialogueExchange with response

# Get NPC info
info = orchestrator.get_npc_info(npc_name)
# Returns: Dict with name, traits, goals, etc.

# List NPCs
npcs = orchestrator.list_npcs()
# Returns: List[str] of NPC names

# Trigger action
action = orchestrator.trigger_npc_action(npc_name, context, "interaction")
# Returns: ActionResponse
```

### Story System Endpoint

```python
# Update story
orchestrator.story_manager.add_plot_point("New plot point")
orchestrator.story_manager.complete_goal("Goal name")
orchestrator.story_manager.update_world_state("key", value)

# Get state
summary = orchestrator.get_story_summary()
state = orchestrator.story_manager.story_state
world_var = orchestrator.story_manager.get_world_state("key")

# Persistence
orchestrator.save_game("save.json")
orchestrator.load_game("save.json")
```

## NPC Creation Template

```python
NPCPersonality(
    name="NPC Name",
    backstory="Detailed background story (1-2 sentences minimum)",
    personality_traits=["trait1", "trait2", "trait3"],
    goals=["goal1", "goal2"],
    relationships={"Other NPC": "relationship description"},
    speech_patterns="How they talk, words they use frequently",
    emotional_state="current mood"
)
```

## Settings

```python
GameSettings(
    llm_model="gpt-4o-mini",        # Model to use
    temperature=0.8,                 # 0.0-2.0, creativity
    max_tokens=500,                  # Response length
    story_style="adventure",         # Genre
    difficulty="medium"              # Challenge
)
```

## Action Types

- `DIALOGUE` - Spoken response
- `MOVEMENT` - Physical movement
- `EMOTION` - Emotional reaction
- `INTERACTION` - Environment interaction
- `STORY_EVENT` - Story advancement

## Examples to Run

```bash
# Basic example
python dialogue_engine/example_usage.py

# Integration demo
python dialogue_engine/demo_integration.py

# Run tests
pytest dialogue_engine/tests/
```

## Common Issues

**Problem:** "Error generating dialogue"
- Check API key in .env
- Verify internet connection
- Try different model

**Problem:** NPC too generic
- Add more personality traits
- Write detailed backstory
- Include speech patterns

**Problem:** Inconsistent NPCs
- Lower temperature (0.5-0.7)
- Add more context
- Define clear goals

## Documentation

- **README.md** - Full API reference
- **GETTING_STARTED.md** - Beginner guide
- **ARCHITECTURE.md** - System design
- **SUMMARY.md** - Project overview

## Key Classes

- `GameOrchestrator` - Main interface
- `StoryManager` - Story system
- `NPCAgent` - NPC behavior
- `NPCPersonality` - NPC definition
- `GameSettings` - Configuration
- `StoryState` - Current story
- `NPCMemory` - Conversation history

## File Structure

```
dialogue_engine/
├── models.py              # Data models
├── orchestrator/          # Player UI endpoint
│   └── game_orchestrator.py
├── agents/                # NPC system
│   └── npc_agent.py
├── story/                 # Story endpoint
│   └── story_manager.py
├── example_usage.py       # Basic example
├── demo_integration.py    # Integration demo
└── tests/                 # Test suite
```

## External Connections

```
Player UI → Game Orchestrator → NPC Agents → LLM API
                ↓
         Story Manager → JSON files
```

---

For more details, see README.md

