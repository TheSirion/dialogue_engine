# Dialogue Engine Architecture

## Overview

The Dialogue Engine is built with a modular architecture that separates concerns between player interaction, NPC behavior, and story management. This design allows for flexible integration and easy extension.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Player UI Layer                        │
│  (Web, Desktop, Mobile, etc.)                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Game Orchestrator                          │
│  • Coordinates all interactions                             │
│  • Manages player input processing                          │
│  • Routes to appropriate NPCs                               │
└───────┬───────────────────────────────────────────┬─────────┘
        │                                           │
        ▼                                           ▼
┌──────────────────────┐              ┌──────────────────────────┐
│    NPC Agent         │              │    Story Manager         │
│                      │              │                          │
│  • Personality       │              │  • Plot State            │
│  • Dialogue Gen      │◄─────────────┤  • Goals                 │
│  • Actions           │   reads      │  • World State           │
│  • Memory            │              │  • History               │
│  • LLM Integration   │              │  • Save/Load             │
└──────────────────────┘              └──────────────────────────┘
        │
        ▼
┌──────────────────────┐
│    LLM Provider      │
│ (Ollama/Open Router) │
└──────────────────────┘
```

## Core Components

### 1. Game Orchestrator

**Location:** `orchestrator/game_orchestrator.py`

**Purpose:** Main entry point and coordinator

**Responsibilities:**
- Accept player input from UI
- Route to appropriate NPCs
- Manage NPC lifecycle
- Coordinate with Story Manager
- Provide unified API for UI

**Key Methods:**
- `process_player_input()` - Main interaction endpoint
- `trigger_npc_action()` - Non-dialogue actions
- `initialize_story()` - Setup story state
- `save_game()` / `load_game()` - Persistence

### 2. NPC Agent

**Location:** `agents/npc_agent.py`

**Purpose:** Individual NPC behavior and dialogue generation

**Responsibilities:**
- Store personality and traits
- Generate contextual dialogue
- Perform actions
- Maintain conversation memory
- Interface with LLM

**Key Methods:**
- `generate_dialogue()` - Create responses
- `generate_action()` - Non-dialogue actions
- `get_memory_summary()` - Memory info
- `update_personality()` - Dynamic changes

**Data Flow:**
```
Player Input + Story Context + Personality → LLM → Dialogue Response
```

### 3. Story Manager

**Location:** `story/story_manager.py`

**Purpose:** Track and manage story state

**Responsibilities:**
- Manage plot points
- Track goals (active/completed)
- Store world state
- Record conversation history
- Handle save/load

**Key Methods:**
- `add_plot_point()` - Story progression
- `complete_goal()` - Goal tracking
- `update_world_state()` - World changes
- `record_conversation()` - History logging

### 4. Data Models

**Location:** `models.py`

**Purpose:** Type-safe data structures

**Key Models:**
- `NPCPersonality` - NPC character definition
- `StoryState` - Current story status
- `NPCMemory` - Conversation history
- `GameSettings` - Configuration
- `ActionResponse` - NPC actions
- `DialogueExchange` - Player-NPC interaction

## Data Flow

### Player Interaction Flow

```
1. Player Input → Player UI
2. Player UI → Game Orchestrator.process_player_input()
3. Orchestrator → NPCAgent.generate_dialogue()
   - Build context (personality, story state, memory)
   - Call LLM API
   - Parse response
4. NPCAgent → Store in memory
5. Orchestrator → Story Manager.record_conversation()
6. Orchestrator → Return DialogueExchange
7. Player UI → Display to player
```

### Story Management Flow

```
1. Game Event → Story System
2. Story System → Story Manager.update_world_state()
3. Story Manager → Update internal state
4. Story Manager → Save to disk (optional)
5. Changed state → Available to NPCs for next dialogue
```

### NPC Action Flow

```
1. Game Event → Orchestrator.trigger_npc_action()
2. Orchestrator → NPCAgent.generate_action()
   - Build context for action
   - Call LLM API
   - Parse action description
3. NPCAgent → Store in memory
4. Orchestrator → Return ActionResponse
```

## Context Building

NPCs generate dialogue using rich context:

```
┌──────────────────────────────────────────────────────────┐
│                    Context Prompt                        │
├──────────────────────────────────────────────────────────┤
│ 1. NPC Background                                        │
│    - Backstory                                           │
│    - Personality traits                                  │
│    - Current emotional state                             │
│                                                          │
│ 2. NPC Goals & Relationships                             │
│    - Personal goals                                      │
│    - Relationships with other NPCs                       │
│                                                          │
│ 3. Story Context                                         │
│    - Current plot points                                 │
│    - Active goals                                        │
│    - World state                                         │
│                                                          │
│ 4. NPC Memories                                          │
│    - Recent interactions                                 │
│    - Important events                                    │
│                                                          │
│ 5. Speech Patterns                                       │
│    - How the NPC talks                                   │
│                                                          │
│ 6. Current Situation                                     │
│    - What the player just said                           │
│    - What's happening                                    │
└──────────────────────────────────────────────────────────┘
           ▼
    LLM API Call
           ▼
    Dialogue Response
```

## Memory System

NPCs remember past interactions:

```
Short-term Memory (< 100 conversations)
├── Recent dialogue exchanges
├── Player input patterns
└── Quick context for continuity

Long-term Memory (important events)
├── Significant story events
├── Relationship changes
└── Goal completions
```

Memory is automatically:
- Stored after each interaction
- Truncated to last 100 exchanges
- Available to future dialogue generation
- Included in context building

## LLM Integration

**Current Support:**
- Open Router
- Ollama (cloud models)

**API Pattern:**
```python
response = client.chat.completions.create(
    model=self.model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context_prompt}
    ],
    temperature=0.8,
    max_tokens=500
)
```

**Extensibility:**
Add new providers by:
1. Creating custom client in `NPCAgent.__init__()`
2. Adapting API call in `generate_dialogue()` / `generate_action()`
3. Adding provider to `GameSettings`

## State Management

### Story State
```python
StoryState:
  - plot_points: List[str]           # Story beats
  - completed_events: List[str]       # Finished events
  - active_goals: List[str]           # Current objectives
  - world_state: Dict[str, Any]       # World variables
  - timestamp: datetime               # Last update
```

### NPC Memory
```python
NPCMemory:
  - npc_name: str                     # Owner
  - memories: List[Dict]              # Conversation history
  - important_events: List[str]       # Notable moments
  - player_interactions: int          # Interaction count
```

### Game Settings
```python
GameSettings:
  - llm_model: str                    # Model to use
  - temperature: float                # Creativity (0-2)
  - max_tokens: int                   # Response length
  - story_style: str                  # Genre
  - difficulty: str                   # Challenge level
```

## Persistence

**Save Format:** JSON
```json
{
  "story_state": {...},
  "npc_memories": {...},
  "conversation_history": [...],
  "settings": {...}
}
```

**Operations:**
- `save_game(filepath)` - Full state export
- `load_game(filepath)` - Full state import
- Atomic (all or nothing)

## Extension Points

### 1. Custom NPC Behaviors

Subclass `NPCAgent`:
```python
class CombatNPC(NPCAgent):
    def generate_combat_dialogue(self, enemy_type):
        # Custom combat-specific dialogue
        pass
```

### 2. Custom Action Types

Extend `ActionType` enum:
```python
ActionType.CUSTOM_ACTION = "custom_action"
```

### 3. Custom Story Events

Add event handlers:
```python
def on_story_event(self, event_type, data):
    # React to story changes
    pass
```

### 4. Custom LLM Providers

Implement provider adapter:
```python
class OllamaProvider:
    def __init__(self, model_name):
        # Setup local LLM
        pass
```

## Design Principles

### 1. Separation of Concerns
- UI layer is independent
- NPCs don't know about story directly
- Story doesn't control NPCs
- Orchestrator coordinates

### 2. Single Responsibility
- Each class has one clear purpose
- Methods do one thing well
- Easy to test and modify

### 3. Loose Coupling
- Components interact through well-defined interfaces
- Changes isolated to modules
- Easy to swap implementations

### 4. High Cohesion
- Related functionality grouped together
- Clear module boundaries
- Logical organization

### 5. Extensibility
- Easy to add new NPCs
- Simple to extend features
- Plugin architecture ready

## Performance Considerations

### 1. LLM API Costs
- **Mitigation:** Use cheaper models for less important NPCs
- **Optimization:** Cache common responses
- **Strategy:** Batch requests when possible

### 2. Memory Management
- Auto-truncate conversation history
- Limit context window size
- Clean up old memories

### 3. Response Time
- Non-blocking UI operations
- Async API calls (future)
- Streaming responses (future)

### 4. Save Performance
- Save to disk only on checkpoints
- Use efficient serialization
- Compress large histories

## Testing Strategy

### Unit Tests
- Test models in isolation
- Verify data validation
- Check state transitions

### Integration Tests
- Test orchestrator-NPC interactions
- Verify story-NPC coordination
- Check save/load reliability

### Acceptance Tests
- End-to-end dialogue flows
- Story progression
- Multiple NPC scenarios

## Future Enhancements

### Planned Features
- [ ] Streaming responses
- [ ] Async API calls
- [ ] Emotion model integration
- [ ] Relationship system expansion
- [ ] Combat dialogue system
- [ ] Multi-language support
- [ ] Voice synthesis integration
- [ ] Character portraits
- [ ] Scene management
- [ ] Branching dialogue trees

### Possible Extensions
- [ ] Reinforcement learning for NPC adaptation
- [ ] Sentiment analysis for emotional responses
- [ ] Procedural content generation
- [ ] Analytics and player behavior tracking
- [ ] Collaborative storytelling
- [ ] Persistent online NPCs

## Summary

The Dialogue Engine provides a clean, modular architecture for creating LLM-powered NPC interactions. Its separation of concerns makes it easy to integrate with any UI while maintaining flexibility for story management and NPC behavior.

Key strengths:
- ✅ Modular design
- ✅ Clear interfaces
- ✅ Easy to extend
- ✅ Well-documented
- ✅ Production-ready structure

The architecture scales from simple dialogue systems to complex narrative experiences.
