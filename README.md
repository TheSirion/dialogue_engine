# Dialogue Engine

A flexible dialogue engine for creating NPC interactions in story-driven games using Large Language Models (LLMs).

## Overview

The Dialogue Engine provides a complete system for managing:
- **NPC Agents**: Intelligent NPCs that generate context-aware dialogue and actions
- **Story Management**: Track plot progression, goals, and world state
- **Player Orchestration**: Coordinate player input with NPC responses and story events

## Architecture

The engine is built with three main components:

### 1. Player UI Orchestrator (`GameOrchestrator`)
The main interface for connecting to player UIs. Handles:
- Player input processing
- NPC response generation
- Setting game configurations
- Managing NPCs
- Coordinating with the story system

### 2. Story System (`StoryManager`)
Tracks and manages:
- Plot points and progression
- Active and completed goals
- World state variables
- Conversation history
- NPC memories
- Save/load game state

### 3. NPC Agents (`NPCAgent`)
Individual NPCs with:
- Personality-based dialogue generation
- Contextual awareness
- Memory of past interactions
- Dynamic actions and responses
- Emotional states

## Features

- **Flexible LLM Integration**: Works with OpenAI GPT models and DeepSeek
- **Personality-Driven**: Each NPC has unique traits, backstory, and speech patterns
- **Story State Tracking**: Comprehensive world state and plot management
- **Memory System**: NPCs remember past interactions and important events
- **Goal Management**: Track and complete story goals
- **Action System**: Generate both dialogue and non-dialogue actions
- **Save/Load**: Persist game state to JSON
- **Extensible**: Easy to add new features and NPCs

## Quick Start

### Installation

Make sure you have the required dependencies installed:

```bash
pip install openai python-dotenv pydantic
```

Set up your API keys in a `.env` file:

```
OPENAI_API_KEY=your_key_here
# OR
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### Basic Usage

```python
from dialogue_engine.orchestrator import GameOrchestrator
from dialogue_engine.models import NPCPersonality, GameSettings

# Create orchestrator
settings = GameSettings(llm_model="gpt-4o-mini", temperature=0.8)
orchestrator = GameOrchestrator(settings)

# Create an NPC
merchant = NPCPersonality(
    name="Merchant Joe",
    backstory="A traveling merchant who knows all the local gossip.",
    personality_traits=["friendly", "talkative", "greedy"],
    goals=["Sell his wares", "Learn market secrets"],
    emotional_state="content"
)

# Add NPC
orchestrator.add_npc(merchant)

# Initialize story
orchestrator.initialize_story(
    plot_points=["The player needs to find a legendary sword"],
    active_goals=["Get information about the sword's location"],
    world_state={"location": "market", "time": "day"}
)

# Process player input
response = orchestrator.process_player_input(
    "Hello, do you know where I can find a legendary sword?",
    "Merchant Joe"
)

print(response.npc_response)
```

### Running the Example

```bash
python dialogue_engine/example_usage.py
```

## API Reference

### GameOrchestrator

Main orchestrator class that coordinates everything.

**Key Methods:**
- `add_npc(personality, model=None)`: Add an NPC to the game
- `process_player_input(text, npc_name)`: Generate NPC response to player
- `trigger_npc_action(npc_name, context, action_type)`: Make NPC perform action
- `initialize_story(plot_points, active_goals, world_state)`: Set up the story
- `save_game(filepath)`: Save current state
- `load_game(filepath)`: Load saved state
- `get_story_summary()`: Get current story status
- `list_npcs()`: Get all NPC names

### NPCPersonality

Defines an NPC's character and behavior.

**Fields:**
- `name`: NPC's name
- `backstory`: Background story
- `personality_traits`: List of traits
- `goals`: What the NPC wants to achieve
- `relationships`: Dictionary of relationship descriptions
- `speech_patterns`: How they talk
- `emotional_state`: Current mood

### GameSettings

Configuration for the game.

**Fields:**
- `llm_model`: Model to use (e.g., "gpt-4o-mini", "deepseek-chat")
- `temperature`: Creativity level (0.0-2.0)
- `max_tokens`: Max response length
- `story_style`: Type of story (adventure, mystery, etc.)
- `difficulty`: Game difficulty level

### StoryManager

Manages story state and progression.

**Key Methods:**
- `set_plot_points(points)`: Define plot points
- `add_active_goal(goal)`: Add a story goal
- `complete_goal(goal)`: Mark goal as done
- `update_world_state(key, value)`: Change world variables
- `record_conversation(...)`: Log dialogue exchange

## Advanced Usage

### Custom NPC Speech Patterns

```python
wizard = NPCPersonality(
    name="Archmage Zephyr",
    backstory="Ancient wizard who speaks in metaphors",
    speech_patterns="Always references nature and the elements. Says 'the winds tell me' frequently. Speaks in third person sometimes.",
    personality_traits=["mysterious", "ancient", "wise"]
)
```

### Managing Story State

```python
# Update world state as the story progresses
orchestrator.story_manager.update_world_state("faction_standing", "neutral")
orchestrator.story_manager.update_world_state("completed_quests", 3)

# Add plot points dynamically
orchestrator.story_manager.add_plot_point("The player uncovered a conspiracy")

# Complete goals
orchestrator.story_manager.complete_goal("Find the ancient artifact")
```

### Using Different LLM Models

```python
# Use OpenAI
settings = GameSettings(llm_model="gpt-4o-mini")

# Use DeepSeek (requires DEEPSEEK_API_KEY in .env)
settings = GameSettings(llm_model="deepseek-chat")

# Use GPT-4 for more complex NPCs
settings = GameSettings(llm_model="gpt-4")
```

### Action Types

NPCs can perform different types of actions:

- `DIALOGUE`: Spoken response
- `MOVEMENT`: Physical movement
- `EMOTION`: Emotional reaction
- `INTERACTION`: Interaction with environment
- `STORY_EVENT`: Story advancement

```python
orchestrator.trigger_npc_action(
    "Aragorn",
    "The party needs to cross a bridge",
    "movement"
)
```

## Integration with UI

The orchestrator provides clean endpoints for UI integration:

```python
# In your web/desktop app

def handle_player_input(self, text, npc_name):
    """Called when player types something"""
    exchange = self.orchestrator.process_player_input(text, npc_name)
    return {
        "npc_name": exchange.npc_name,
        "response": exchange.npc_response,
        "emotional_state": exchange.emotional_state,
        "timestamp": exchange.timestamp.isoformat()
    }

def update_story_state(self, key, value):
    """Called when story state changes"""
    self.orchestrator.story_manager.update_world_state(key, value)

def get_game_state(self):
    """Get current game state for UI rendering"""
    return {
        "story_summary": self.orchestrator.get_story_summary(),
        "npcs": self.orchestrator.list_npcs(),
        "world_state": self.orchestrator.story_manager.story_state.world_state
    }
```

## Extending the Engine

### Custom NPC Behaviors

Subclass `NPCAgent` to add custom behavior:

```python
from dialogue_engine.agents import NPCAgent

class MerchantNPC(NPCAgent):
    def generate_trade_dialogue(self, item_name, price):
        """Generate dialogue when trading"""
        # Custom trading logic
        pass
```

### Custom Actions

Add new action types by extending `ActionType`:

```python
from dialogue_engine.models import ActionType
ActionType.COMPUTER_INTERACTION = "computer_interaction"
```

## Best Practices

1. **Temperature Settings**: 
   - 0.5-0.7 for consistent NPCs
   - 0.8-1.0 for creative/chaotic NPCs

2. **Memory Management**: The system keeps last 100 conversations automatically

3. **NPC Design**: Give NPCs clear goals and relationships for better interactions

4. **Story Pacing**: Add plot points gradually as the story progresses

5. **Save Frequency**: Save after major story events

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

