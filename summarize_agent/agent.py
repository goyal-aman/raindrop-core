from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from summarize_agent.prompts import summarizer_agent_prompt_v1
from google.adk.runners import Runner
from google.genai.types import Content, Part
from summarize_agent.tools import get_article_content_from_url
from dotenv import load_dotenv
import os

# 1. Get your Firecrawl API key (best to use environment variables)
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")


summarizer_agent = Agent(
    model = 'gemini-2.5-flash',
    name = 'summarizer_agent',
    description='a helpful assistant for summarizing articles into markdown',
    instruction=summarizer_agent_prompt_v1,
    tools=[get_article_content_from_url]
)


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[
        AgentTool(agent=summarizer_agent)
    ]
)


