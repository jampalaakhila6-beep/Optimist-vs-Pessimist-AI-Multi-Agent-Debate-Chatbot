import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

# -------------------------------

# Load Environment Variables

# -------------------------------

load_dotenv()

# -------------------------------

# Gemini Model

# -------------------------------

model_client = OpenAIChatCompletionClient(
model="gemini-2.5-flash",
api_key=os.getenv("GEMINI_API_KEY"),
base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
model_info={
"vision": True,
"function_calling": True,
"json_output": True,
"structured_output": True,
"family": "unknown"
}
)

# -------------------------------

# Optimistic Friend

# -------------------------------

over_optimistic_agent = AssistantAgent(
"over_optimistic_friend",
model_client=model_client,
system_message="""
You are the user's extremely over-optimistic best friend.

The user and their crush can be of any gender. Never assume gender unless the user mentions it.

Rules:

* Always assume every interaction is a positive sign.
* Be energetic, funny, dramatic, and supportive.
* Convince the user that their crush likes them (playfully, not as a fact).
* Counter the negative friend's arguments.
* Mix English with Telugu written in English naturally (e.g., "Arey bro!", "Ammo!", "Scene bagundi!").
* Use emojis occasionally (😂😎🔥).
* **Reply in exactly 2 short sentences only.**
  """
  )

# -------------------------------

# Negative Friend

# -------------------------------

negative_agent = AssistantAgent(
"negative_friend",
model_client=model_client,
system_message="""
You are the user's brutally pessimistic but funny best friend.

The user and their crush can be of any gender. Never assume gender unless the user mentions it.

Rules:

* Always give a logical explanation.
* Counter the optimistic friend's arguments.
* Be sarcastic and funny without insulting the user.
* Mix English with Telugu written in English naturally (e.g., "Bro...", "Cinema kaadu idi.", "Konchem reality loki ra.").
* Use emojis occasionally (🙄😂🤦).
* **Reply in exactly 2 short sentences only.**
  """
  )

# -------------------------------

# Group Chat

# -------------------------------

termination = MaxMessageTermination(max_messages=4)

team = RoundRobinGroupChat(
participants=[over_optimistic_agent, negative_agent],
termination_condition=termination,
)

# -------------------------------

# Run Agents

# -------------------------------

async def run_agents(user_input):
    responses = []

    async for msg in team.run_stream(task=user_input):

        if hasattr(msg, "source") and hasattr(msg, "content"):
            responses.append({
                "agent": msg.source,
                "content": msg.content
            })

    return responses

# -------------------------------

# Streamlit UI

# -------------------------------

st.set_page_config(
page_title="The Analyzers",
page_icon="😂",
layout="centered"
)

st.title("😂 Optimist vs Pessimist Analyzers")

st.markdown(
"Describe what happened and let the agents debate!"
)

user_input = st.text_area(
"Tell us what happened",
placeholder="Type something...."
)

if st.button("Analyze"):
    try:
        with st.spinner("Agents are debating..."):
            result = asyncio.run(run_agents(user_input))

        st.success("Debate Finished!")

        for response in result:
            if response["agent"] == "over_optimistic_friend":
                st.success(f"😎 Optimistic Friend\n\n{response['content']}"
                )

            elif response["agent"] == "negative_friend":
                st.error(f"😒 Negative Friend\n\n{response['content']}"
                )

    except Exception as e:
        st.error(str(e))
        print("FULL ERROR:", e)