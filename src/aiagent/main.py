import asyncio
import re
import time
import warnings

import edge_tts
import pygame

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

console = Console()

warnings.filterwarnings(
    "ignore",
    message=r"Model .* uses fixed sampling defaults.*",
    category=UserWarning
)

session_state = {
    "voice_enabled": True,
    "quit_requested": False
}

pygame.mixer.init()
load_dotenv()



@tool
def set_voice(enabled: bool)-> str:
    """Enable or disable spoken responses when the user asks to change voice output."""
    session_state["voice_enabled"] = enabled

    if enabled:
        return "Voice output is now enabled."
    return "Voice output is now disabled."

@tool
def exit_friday()-> str:
    """Exit FRIDAY when the user clearly wants to end the assistant session."""
    session_state["quit_requested"] = True
    return "The user has requested to exit the FRIDAY."

def type_text(text, delay = 0.015):
    """Display text one character at a time."""

    for character in text:
        print(character, end="", flush=True)
        time.sleep(delay)
    print()



def clean_text(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'[*_~#]+', '', text)
    text = re.sub(r'(?m)^\s*[-+>]\s+', '', text)
    text = re.sub(r'(?m)^\s*\d+\.\s+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text



async def speak(text):
    filename = "friday_voice.mp3"

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except pygame.error:
        pass

    communicate = edge_tts.Communicate(
        text, 
        voice = "en-GB-RyanNeural"
    )

    await communicate.save(filename)



def show_startup():
    console.clear()

    title = Text(
        "F.R.I.D.A.Y.\nPersonal Intelligence System",
        justify="center",
        style="bold cyan"
    )

    console.print(
        Panel(
            title,
            title="[bold blue]STARK INTERFACE[/bold blue]",
            subtitle="[green]● ALL SYSTEMS ONLINE[/green]",
            border_style="bright_cyan",
            padding=(2, 4)
        )
    )

    console.print("[cyan]AI Core:[/cyan] [green]Active[/green]")
    console.print("[cyan]Memory:[/cyan] [green]Connected[/green]")
    console.print("[cyan]Voice:[/cyan] [green]Ready[/green]")
    console.print()



def main():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature = 0.7
    )

    tools = [set_voice, exit_friday]

    system_prompt = """
    You are FRIDAY, a highly intelligent personal AI assistant inspired
    by the AI assistant from Iron Man.

    PERSONALITY:
    - Be friendly, warm, confident, and professional.
    - Speak naturally, like a helpful companion, not a robot.
    - Be intelligent, calm, and slightly witty when appropriate.
    - Be respectful and supportive.
    - Make the user feel comfortable asking any question.
    - Remember the conversation context provided in the current session.
    - Never sound unnecessarily formal or repetitive.

    SPEAKING STYLE:
    - Use clear, natural English.
    - Prefer concise answers, but explain things when needed.
    - Occasionally use expressions such as:
      "Certainly."
      "Of course."
      "Right away."
      "I'd be happy to help."
      "Here's what I've found."
    - Use these expressions naturally, not in every response.
    - Address the user as "sir" occasionally, but do not overuse it.
    - Use subtle, intelligent humor when appropriate.
    - Never claim to have performed an action you have not performed.

    ASSISTANT BEHAVIOR:
    - Help with programming, calculations, learning, and everyday questions.
    - Explain technical concepts in beginner-friendly language when needed.
    - If you do not know something, be honest about it.
    - Ask a friendly follow-up question only when it is useful.

    You should have the conversational feel of a sophisticated,
    British-inspired AI assistant: composed, articulate, friendly,
    and subtly humorous.

    NATURAL LANGUAGE CONTROLS:
    - Understand the user's intention, not just exact commands.
    - If the user clearly wants to stop hearing spoken responses,
      use set_voice(enabled=False).
    - If the user clearly wants spoken responses enabled,
      use set_voice(enabled=True).
    - If the user clearly wants to end the FRIDAY session,
      use exit_friday().
    - Do not trigger these actions when the user is merely discussing
      muting, voice settings, or quitting in a different context.
    - Confirm actions naturally and briefly.
    - Never exit the application just because the user says goodbye
      to someone else or mentions quitting something unrelated.
    """
    with SqliteSaver.from_conn_string("friday_memory.sqlite") as memory:

        agent_executor = create_agent(model, tools, system_prompt=system_prompt, checkpointer = memory)

        config = {
            "configurable": {
                "thread_id": "friday_main_session"
            }
        }

        show_startup()
        console.print("[bold cyan]FRIDAY:[/bold cyan] Good day, sir. How may I assist you?")
        console.print("[dim]Speak naturally. Press Ctrl+C to exit.[/dim]\n")

        while True:
            try:
                user_input = Prompt.ask("\n[bold bright_cyan]YOU ❯[/bold bright_cyan]").strip()
            except(EOFError, KeyboardInterrupt):
                print("\n")
                type_text("FRIDAY: Signing off. Until next time.")
                break

            if not user_input:
                continue

            try:
                with console.status(
                    "[bold cyan]FRIDAY is thinking...[/bold cyan]",
                    spinner="dots"
                ):
                    result = agent_executor.invoke(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=config
                    )

                response = None

                for message in reversed(result["messages"]):
                    if message.type == "ai" and message.content:
                        if isinstance(message.content, str):
                            response = message.content
                        else:
                            text_parts = [
                                item["text"]
                                for item in message.content
                                if isinstance(item, dict)
                                and item.get("type") == "text"
                            ]

                            response = "\n".join(text_parts)
                            
                        if response:
                            break

                if response:
                    clean_response = clean_text(response)

                    console.print("\n[bold bright_cyan]FRIDAY ❯[/bold bright_cyan] ", end="")

                    if session_state["voice_enabled"]:
                        try:
                            asyncio.run(speak(clean_response))

                            pygame.mixer.music.load("friday_voice.mp3")
                            pygame.mixer.music.play()

                            type_text(clean_response)

                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)

                            pygame.mixer.music.unload()

                        except (OSError, RuntimeError, TimeoutError, ValueError) as e:
                            print(f"[Voice error: {e}]")
                            type_text(clean_response)
                    else:
                        type_text(clean_response)

            except (ConnectionError, TimeoutError, ValueError, RuntimeError) as error:
                print(f"\nFRIDAY: I'm afraid something went wrong: {error}")
                print("Please check your connection and try again.\n")

            
            if session_state["quit_requested"]:
                print("\nFRIDAY: Until next time. Have a wonderful day!")
                break



if __name__ == "__main__":
    main()
