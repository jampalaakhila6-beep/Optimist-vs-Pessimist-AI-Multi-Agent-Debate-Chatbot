from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv

load_dotenv()

model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY")
)