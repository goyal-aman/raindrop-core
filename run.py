from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService

from google.adk.tools.agent_tool import AgentTool
from summarize_agent.prompts import summarizer_agent_prompt_v1
from google.adk.runners import Runner
from google.genai.types import Content, Part

from summarize_agent.agent import root_agent

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)


APP_NAME = "summarize-agent"

session_service = InMemorySessionService()

async def main(user_id: str, session_id: str, url: str):
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )


    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    user_content = Content(
            role="user", parts=[Part(text=url)]
        )
    
    final_response_content = "No response"
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = ''.join(part.text for part in event.content.parts)


    return final_response_content

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(
        main(
            user_id="random", 
            session_id="random", 
            # url = "https://www.mongodb.com/company/blog/engineering/to-lock-or-not-mongodbs-lock-free-b-tree-unlocks-throughput"
            url = "https://blog.stackademic.com/how-to-implement-cache-in-your-golang-api-cea87a260e21"
    ))
    print(result)