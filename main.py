from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from whatsApp import send_whatsApp_message
import asyncio
import chainlit as cl
import re

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# ✅ Improved get_user_data tool
@function_tool
def get_user_data(min_age: int) -> list[dict]:
    """Retrieve user data based on a minimum age"""
    users = [
        {"name": "Muneeb", "age": 22},
        {"name": "Soaib", "age": 26},
        {"name": "Sarim", "age": 24},
        {"name": "Areeba", "age": 20},
        {"name": "Zainab", "age": 27},
        {"name": "Ali", "age": 19},
        {"name": "Hira", "age": 23},
        {"name": "Muneeb", "age": 21},
        {"name": "Hassan", "age": 25},
        {"name": "Fatima", "age": 28},
    ]
    return [user for user in users if user["age"] >= min_age]

# ✅ Matchmaker Agent
rishty_agent = Agent(
    name="Rishty_wali",
    instructions="""
        You are best Match Maker. Help users find rishtas above a given age using `get_user_data`.
        If user requests to send the result on WhatsApp, call `send_whatsApp_message`.
        Reply in short friendly tone.
    """,
    model=model,
    tools=[get_user_data, send_whatsApp_message]
)

# ✅ Extract age and WhatsApp number from input
def extract_age_and_number(text):
    age_match = re.search(r'\b(\d{2})\b', text)
    phone_match = re.search(r'03\d{9}', text)

    age = int(age_match.group(1)) if age_match else None
    number = phone_match.group(0) if phone_match else None

    return age, number

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message("🌸 Assalam o Alaikum! I am your best Match Maker.\nGive me Your **Age** and **WhatsApp number**, I will search best match for you!").send()

# ✅ Main runner
@cl.on_message
async def main(message: cl.Message):
    await cl.Message("🧠 Thinking...").send()

    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})

    # extract user info
    age, number = extract_age_and_number(message.content)
    cl.user_session.set("user_age", age)
    cl.user_session.set("user_number", number)

    # 🤖 Run agent
    result = Runner.run_sync(
        starting_agent=rishty_agent,
        input=history
    )

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    await cl.Message(content=result.final_output).send()

    # ✅ Check if user wants WhatsApp delivery
    if "whatsapp" in message.content.lower() and age and number:
        tools=[get_user_data, send_whatsApp_message]
        matches = get_user_data(age)
        match_text = "\n".join([f"{u['name']} ({u['age']} yrs)" for u in matches])
        response = send_whatsApp_message(number, f"Here are your matches:\n{match_text}")
        await cl.Message(f"📲 {response}").send()
        
