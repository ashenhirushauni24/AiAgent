import sys
import time

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
import warnings

warnings.filterwarnings(
    "ignore",
    message="Model .* uses fixed sampling defaults.*",
    category=UserWarning
)

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

def main():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature = 0/7
    )

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
                    print("\nFRIDAY: ", end="", flush=True)
                    type_text(response)
                    print()

            except Exception as error:
                print(f"\nFRIDAY: I'm afraid something went wrong: {error}")
                print("Please check your connection and try again.\n")

if __name__ == "__main__":
    main()
