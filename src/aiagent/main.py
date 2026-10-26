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

warnings.filterwarnings(
    "ignore",
    message="Model .* uses fixed sampling defaults.*",
    category=UserWarning
)

pygame.mixer.init()
load_dotenv()



@tool
def calculator(a: float, b: float) -> str:
    """Useful for performing basic arithmetic calculations with numbers"""
    print("\n[FRIDAY is calculating...]")
    return f"The sum of {a} and {b} is {a+b}"



def type_text(text, delay = 0.015):
    """Display text one character at a time."""

    for character in text:
        print(character, end="", flush=True)
        time.sleep(delay)
    print()



def clean_text(text):
    # Remove Markdown links but keep their visible text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove code blocks and inline code markers
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # Remove bold, italic, strikethrough and heading markers
    text = re.sub(r'[*_~#]+', '', text)

    # Remove Markdown list and quote markers
    text = re.sub(r'(?m)^\s*[-+>]\s+', '', text)
    text = re.sub(r'(?m)^\s*\d+\.\s+', '', text)

    # Remove repeated whitespace
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



def main():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature = 0/7
    )

    voice_enabled = True
    tools = [calculator]

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
    - Use the calculator tool whenever an actual calculation is useful.
    - If you do not know something, be honest about it.
    - Ask a friendly follow-up question only when it is useful.

    You should have the conversational feel of a sophisticated,
    British-inspired AI assistant: composed, articulate, friendly,
    and subtly humorous.
    """
    with SqliteSaver.from_conn_string("friday_memory.sqlite") as memory:

        agent_executor = create_agent(model, tools, system_prompt=system_prompt, checkpointer = memory)

        config = {
            "configurable": {
                "thread_id": "friday_main_session"
            }
        }

        print()
        type_text("FRIDAY: Good day! Systems are online.")
        type_text("FRIDAY: How may I assist you today?")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except(EOFError, KeyboardInterrupt):
                print("\n")
                type_text("FRIDAY: Signing off. Until next time.")
                break

            if user_input == "quit":
                print("\nFRIDAY: Until next time. Have a wonderful day!")
                break

            if not user_input:
                continue

            if user_input.lower() == "voice off":
                voice_enabled = False
                print("FRIDAY: Voice output disabed.")
                continue

            if user_input.lower() == "voice on":
                voice_enabled = True
                print("FRIDAY: Voice output enabled.")
                continue

            try:
                result = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)

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

                    print("\nFRIDAY: ", end="", flush=True)

                    if voice_enabled:
                        try:
                            asyncio.run(speak(clean_response))

                            pygame.mixer.music.load("friday_voice.mp3")
                            pygame.mixer.music.play()

                            type_text(clean_response)
                            print()

                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)

                            pygame.mixer.music.unload()

                        except (OSError, RuntimeError, TimeoutError, ValueError) as e:
                            print(f"[Voice error: {e}]")
                    else:
                        type_text(clean_response)
                        print()

            except (ConnectionError, TimeoutError, ValueError, RuntimeError) as error:
                print(f"\nFRIDAY: I'm afraid something went wrong: {error}")
                print("Please check your connection and try again.\n")



if __name__ == "__main__":
    main()
