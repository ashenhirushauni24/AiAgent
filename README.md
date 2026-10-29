# F.R.I.D.A.Y. — Personal AI Assistant

> A Python-based AI assistant inspired by the intelligent personal assistant from Iron Man.

FRIDAY is my first AI agent project, built with Python and Google's Gemini models. It combines conversational AI, persistent conversation memory, natural-language controls, text-to-speech, and a modern terminal interface to create a more interactive assistant experience.

## ✨ Features

- **AI-powered conversations** — Uses Google Gemini through LangChain.
- **Persistent conversation memory** — Uses SQLite and LangGraph checkpointing to preserve conversation state across restarts.
- **Natural-language controls** — Ask FRIDAY to enable or disable voice output or shut down without memorising exact commands.
- **British English voice** — Generates spoken responses using Edge TTS.
- **Audio playback** — Uses Pygame to play generated speech.
- **Typing animation** — Displays responses with a character-by-character effect.
- **Modern CLI interface** — Uses Rich for coloured text, startup panels, and animated thinking indicators.
- **Markdown cleanup** — Removes common Markdown formatting before displaying or speaking responses.
- **Gemini error handling** — Handles common connection and runtime errors.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Google Gemini | Language model |
| LangChain | Agent creation and tool integration |
| LangGraph | Agent state and checkpointing |
| SQLite | Persistent conversation storage |
| Edge TTS | Text-to-speech generation |
| Pygame | Audio playback |
| Rich | Terminal styling and animations |
| uv | Python project and dependency management |
| python-dotenv | Environment variable loading |

## 📋 Prerequisites

Before running FRIDAY, make sure you have:

- Windows 10 or Windows 11, or another supported operating system.
- A compatible Python version.
- [uv](https://docs.astral.sh/uv/) installed.
- A Google Gemini API key.
- An internet connection for Gemini requests and Edge TTS generation.
- Working audio output if you want to use voice features.

## 🚀 Installation

### 1. Clone the repository

If the project is hosted on GitHub:

```bash
git clone YOUR_REPOSITORY_URL
cd AiAgent
```

Replace `YOUR_REPOSITORY_URL` with your actual repository URL.

Alternatively, open your existing project directory in VS Code.

### 2. Install dependencies

If your project already has a `pyproject.toml` file, run:

```bash
uv sync
```

If you are setting up the project from scratch, initialise it with uv and install the required packages:

```bash
uv init
uv add langchain langgraph langchain-google-genai langgraph-checkpoint-sqlite python-dotenv edge-tts pygame rich
```

Install any additional packages required by your existing code.

### 3. Configure environment variables

Create a file named `.env` in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Replace the example value with your own API key.

Ensure that your application loads the environment variables:

```python
from dotenv import load_dotenv

load_dotenv()
```

**Security:** Never commit your `.env` file or expose your API key in a public repository. Add `.env` to `.gitignore`.

### 4. Run FRIDAY

If your entry-point file is `main.py`, run:

```bash
uv run main.py
```

FRIDAY should initialise its terminal interface and become ready for conversation.

## 💬 Usage

FRIDAY is designed to understand natural language rather than require users to memorise commands.

Examples of things you can say:

| Request | Expected behaviour |
|---|---|
| "Hello, FRIDAY." | Starts a conversation |
| "Could you stop speaking aloud?" | Disables voice output if the agent recognises the intent |
| "Please speak to me again." | Enables voice output if the agent recognises the intent |
| "That's everything for today. You can shut down." | Requests application shutdown if the intent is recognised |
| "Can you calculate 25 plus 75?" | Performs the calculation if the calculator tool is enabled |

The precise wording is flexible. The available actions depend on the tools registered with the agent.

Press `Ctrl+C` to interrupt the application.

## 🧠 How Memory Works

FRIDAY uses LangGraph's SQLite checkpointer to preserve conversation state.

The application initialises the checkpointer with:

```python
with SqliteSaver.from_conn_string("friday_memory.sqlite") as memory:
    ...
```

The database file is created relative to the application's current working directory unless an absolute path is configured.

The agent uses a thread identifier to resume the same conversation:

```python
config = {
    "configurable": {
        "thread_id": "friday_main_session"
    }
}
```

Reusing the same thread ID allows FRIDAY to retrieve saved conversation state across restarts.

**Important:** SQLite checkpointing stores conversation state; it is not a complete personal-memory system. Voice settings stored only in a Python dictionary reset when the application restarts.

Back up the database before making changes or resetting conversation history.

## 📁 Project Structure

An illustrative structure for this project is:

```text
AiAgent/
├── main.py
├── friday_memory.sqlite
├── friday_voice.mp3
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

Some files are generated at runtime. The SQLite database and audio file may not exist until FRIDAY has been run.

The `.env` file contains secrets and must not be committed. The `.venv` directory, generated audio files, and local database may also be excluded from Git, depending on whether you want to share them.

## ⚙️ Configuration

### Change the voice

The current voice configuration uses:

```python
voice="en-GB-RyanNeural"
```

You can change this to another supported Edge TTS voice.

### Adjust typing speed

The typing animation is controlled by the delay:

```python
def type_text(text, delay=0.015):
    ...
```

A smaller delay makes the animation faster; a larger delay makes it slower.

### Change the conversation thread

Modify the thread ID in the configuration to start a separate conversation thread:

```python
"thread_id": "friday_main_session"
```

Use a different ID when you intentionally want a separate conversation history.

## 🧰 Troubleshooting

**Gemini API errors**
- Check that your API key is valid.
- Confirm that `.env` is in the expected directory.
- Verify your internet connection and API access.

**Audio permission errors**
- Stop or unload the currently playing audio before replacing the MP3 file.
- Ensure that no other application is locking the audio file.

**No spoken response**
- Check that voice output is enabled.
- Verify that Pygame initialised successfully and your audio output works.
- Confirm that Edge TTS can connect to the internet.

**SQLite memory appears missing**
- Check the current working directory.
- Confirm that the application uses the intended database path and thread ID.
- Ensure the database file has not been moved or deleted.

**Missing packages**

```bash
uv sync
```

If a dependency is missing from the project configuration, add it with `uv add package-name`.

## 🔒 Privacy and Security

- Keep API keys in environment variables.
- Do not upload secrets or credentials to GitHub.
- Treat conversation databases as potentially sensitive because they may contain previous messages.
- Review which generated files should be included in version control.

## 🎯 Future Improvements

Ideas for future development include:

- More tools for everyday computer tasks.
- A configurable voice and appearance system.
- Improved speech and text synchronisation.
- Better long-term memory for useful facts and preferences.
- A richer interactive terminal dashboard.
- Additional error recovery and testing.

## 👨‍💻 About This Project

FRIDAY is my first AI agent project and part of my journey in learning Python, AI agents, and practical software development.

Building it has helped me explore language models, tool calling, conversation state, text-to-speech, and terminal user interfaces.

This project will continue to evolve as I learn and add new capabilities.

---

*Built with Python, curiosity, and a little inspiration from Stark Industries.* 
