# Tang Dynasty Dialogue System

A Tang Dynasty educational dialogue game with three NPC branches: 雷班主, 安掌櫃, and 裴掌櫃. `final.html` is served by a small Python backend so free-text dialogue can safely call Gemini with server-side system prompts.

## Project Structure

```
.
├── src/                    # Core application code
│   ├── __init__.py
│   └── models.py          # Core data models
├── config/                # Configuration files
│   └── __init__.py
├── frontend/              # Frontend interface code
│   └── __init__.py
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_models.py    # Data model tests
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your API key:

```bash
cp .env.example .env
```

Edit `.env` and set one Google Gemini API key per NPC branch:

```
GEMINI_API_KEY_THEATER=your_theater_npc_api_key_here
GEMINI_API_KEY_FOOD=your_food_npc_api_key_here
GEMINI_API_KEY_TBD=your_tbd_npc_api_key_here
```

### 5. Run the Web Game

```bash
python app.py
```

Open `http://localhost:8000`.

The frontend calls `POST /api/dialogue`; do not put a Gemini API key in `final.html`. If Gemini quota is exhausted, the model is unavailable, the key is missing, or the network fails, the API returns:

```json
{
  "npc_response": "回覆額度用盡，請選既有選項",
  "is_fallback": true
}
```

In that fallback state, the game keeps the existing A/B choices available and does not open the science popup.

## Deployment

For one public playable URL, deploy this repo as a Python web service on Render, Railway, Fly.io, Cloud Run, or a similar host.

- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Required environment variables: `GEMINI_API_KEY_THEATER`, `GEMINI_API_KEY_FOOD`, `GEMINI_API_KEY_TBD`
- Optional fallback environment variable: `GEMINI_API_KEY`
- Optional environment variables: `GEMINI_MODEL` or `MODEL_NAME` (default: `gemini-3.1-flash-lite`), `PORT`

GitHub Pages alone can host only the static `final.html`; it cannot safely run the Python backend or protect the API key.

## Core Data Models

### TurnNumber (Enum)
- `TURN_1`: Food cooking and preservation
- `TURN_2`: Clothing materials and fastening
- `TURN_3`: Clothing colors and social hierarchy

### ConversationState
Tracks the current dialogue state:
- `current_turn`: Current turn number (1-3)
- `is_complete`: Whether all three turns are finished
- `conversation_history`: List of (player_input, npc_response) tuples
- `timestamp`: ISO format timestamp of last update

### DialogueResponse
Response returned to frontend:
- `npc_response`: An Shopkeeper's dialogue text
- `turn`: Current turn number
- `knowledge_window`: Educational content
- `is_complete`: Conversation completion status

### KnowledgeWindow
Educational content displayed after convergence:
- `title`: Window title
- `body`: Educational content in markdown
- `image_description`: Suggested image for visual display

### SystemConfig
System configuration loaded from environment:
- `api_key`: Google Gemini API key
- `model_name`: LLM model name (default: gemini-3.1-flash-lite)
- `max_input_length`: Maximum player input length (default: 500)
- `storage_backend`: Storage type (file/memory/database)
- `temperature`: LLM sampling temperature (default: 0.7)
- `max_tokens`: Maximum response length (default: 500)

## Serialization

All data models support serialization:
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary
- `to_json()`: Convert to JSON string

## Running Tests

```bash
pytest tests/ -v
```

## Requirements Validated

This implementation validates the following requirements:
- **5.1**: Structured response data containing NPC dialogue text
- **5.2**: Structured response data containing current turn number
- **5.3**: Structured response data containing Knowledge_Window content
- **5.4**: Structured response data containing conversation completion status
- **5.5**: Structured response data in JSON format
- **5.6**: Knowledge_Window content includes title, body text, and image descriptions
- **12.1**: NPC-specific API keys read from environment variables or .env file
- **12.2**: LLM model name configurable via environment variable
- **12.3**: Maximum input length configurable via environment variable
- **12.4**: State persistence method configurable via environment variable
- **12.5**: Clear error message when required environment variables are missing

## Next Steps

1. Implement StateManager for state persistence
2. Implement ResponseGenerator for LLM integration
3. Implement PromptManager for prompt engineering
4. Implement KnowledgeWindowProvider for educational content
5. Implement DialogueSystem core orchestrator
6. Implement TerminalInterface for testing
7. Create HTML/JavaScript frontend
