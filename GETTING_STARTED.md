# Getting Started with Dialogue Engine

Quick guide to get up and running with the Dialogue Engine.

## Prerequisites

- Python 3.8+
- OpenAI API key OR DeepSeek API key
- Basic familiarity with Python

## Installation

### 1. Install Dependencies

```bash
pip install -r dialogue_engine/requirements.txt
```

Or install individually:

```bash
pip install openai python-dotenv pydantic
```

### 2. Set Up API Keys

Create a `.env` file in your project root:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# OR for DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Quick Start Example

Copy this code to a new file `quick_start.py`:

```python
from dialogue_engine.orchestrator import GameOrchestrator
from dialogue_engine.models import NPCPersonality, GameSettings

# Create game
settings = GameSettings(llm_model="gpt-4o-mini", temperature=0.8)
game = GameOrchestrator(settings)

# Create an NPC
innkeeper = NPCPersonality(
    name="Old Tom",
    backstory="An elderly innkeeper with decades of stories",
    personality_traits=["kind", "talkative", "wise"],
    goals=["Welcome travelers", "Share local lore"],
    emotional_state="welcoming"
)

game.add_npc(innkeeper)

# Set up story
game.initialize_story(
    plot_points=["The player arrives at a peaceful inn"],
    active_goals=["Rest and gather information"],
    world_state={"location": "inn", "atmosphere": "cozy"}
)

# Have a conversation
response = game.process_player_input(
    "Hello! This place looks wonderful.",
    "Old Tom"
)

print(f"\nPlayer: Hello! This place looks wonderful.")
print(f"Old Tom: {response.npc_response}")
```

Run it:

```bash
python quick_start.py
```

## Running the Full Examples

### Basic Example

```bash
python dialogue_engine/example_usage.py
```

This demonstrates:
- Setting up NPCs with personalities
- Managing story state
- Player-NPC dialogue
- NPC actions
- Saving game state

### Integration Demo

```bash
python dialogue_engine/demo_integration.py
```

This shows how to:
- Connect a Player UI interface
- Use the Story System endpoint
- Manage game state separately from dialogue
- Save and load games

## Common Use Cases

### Creating Different Types of NPCs

**Friendly NPC:**
```python
friendly = NPCPersonality(
    name="Sarah",
    backstory="A helpful villager",
    personality_traits=["friendly", "helpful", "optimistic"],
    speech_patterns="Very cheerful, uses lots of exclamation points!"
)
```

**Mysterious NPC:**
```python
mysterious = NPCPersonality(
    name="The Oracle",
    backstory="An ancient seer who speaks in riddles",
    personality_traits=["mysterious", "wise", "cryptic"],
    speech_patterns="Speaks in vague metaphors. Never gives direct answers."
)
```

**Hostile NPC:**
```python
hostile = NPCPersonality(
    name="Brutus",
    backstory="A guard who doesn't like strangers",
    personality_traits=["suspicious", "aggressive", "loyal"],
    speech_patterns="Speaks gruffly. Uses threats and ultimatums."
)
```

### Managing Story Flow

```python
# Add plot points as story progresses
game.story_manager.add_plot_point("The artifact glows with strange energy")

# Update world state
game.story_manager.update_world_state("player_has_artifact", True)

# Complete goals
game.story_manager.complete_goal("Find the ancient artifact")

# Check state
player_has_artifact = game.story_manager.get_world_state("player_has_artifact")
```

### Using Different LLM Models

```python
# OpenAI GPT-4
settings = GameSettings(llm_model="gpt-4o-mini", temperature=0.7)

# OpenAI GPT-4 (more powerful, more expensive)
settings = GameSettings(llm_model="gpt-4", temperature=0.7)

# DeepSeek (if you have API key)
settings = GameSettings(llm_model="deepseek-chat", temperature=0.8)

game = GameOrchestrator(settings)
```

### Adjusting Creativity

```python
# More consistent NPCs
settings = GameSettings(temperature=0.5)

# Creative but coherent
settings = GameSettings(temperature=0.8)

# Very creative (may be inconsistent)
settings = GameSettings(temperature=1.2)
```

## Tips for Best Results

### 1. Write Detailed Backgrounds

Better backstories = better dialogue:

```python
# ❌ Too vague
NPCPersonality(backstory="A guard", ...)

# ✅ Detailed and interesting
NPCPersonality(
    backstory="A veteran of three wars, now serves as city guard. Lost his left eye in the Great Battle. Has a wife and two kids at home.",
    ...
)
```

### 2. Define Clear Goals

NPCs with goals feel more alive:

```python
NPCPersonality(
    goals=[
        "Protect the city gate",
        "Avenge his fallen comrades",
        "Provide for his family"
    ],
    ...
)
```

### 3. Use Speech Patterns

This makes NPCs unique and memorable:

```python
NPCPersonality(
    speech_patterns="Uses military terminology. Says 'sir' frequently. Speaks formally.",
    ...
)
```

### 4. Track Important Story Events

```python
# When something important happens
game.story_manager.complete_event("player_retrieved_artifact")
game.story_manager.update_world_state("artifact_location", "player_inventory")
```

### 5. Save Frequently

```python
# After major story beats
game.save_game("auto_save.json")

# Or regular saves
game.save_game(f"save_slot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
```

## Troubleshooting

### "Error generating dialogue"

**Problem:** LLM API call failed

**Solutions:**
- Check your API key is set correctly in `.env`
- Verify you have API credits
- Try a different model (e.g., `gpt-4o-mini` instead of `gpt-4`)
- Check your internet connection

### NPC responses are too generic

**Solutions:**
- Add more detailed personality traits
- Include more specific backstory
- Set speech patterns
- Define clear goals
- Increase context in story state

### NPCs are inconsistent

**Solutions:**
- Lower temperature (0.5-0.7)
- Provide more story context
- Use more detailed personalities
- Ensure goals and relationships are clear

### API costs too high

**Solutions:**
- Use `gpt-4o-mini` instead of `gpt-4`
- Use DeepSeek (often cheaper)
- Reduce `max_tokens` in settings
- Cache common responses
- Use a local model with Ollama (requires custom integration)

## Next Steps

1. **Read the README.md** for complete API reference
2. **Run the examples** to see features in action
3. **Experiment** with different personalities and scenarios
4. **Build your UI** connecting to the orchestrator endpoints
5. **Extend the system** with custom behaviors

## Need Help?

- Check the examples in `dialogue_engine/example_usage.py`
- Read the API docs in `dialogue_engine/README.md`
- Review the integration demo in `dialogue_engine/demo_integration.py`
- Look at the code - it's well-commented!

Happy storytelling! 🎭✨

