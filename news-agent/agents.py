import asyncio
import sys

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

load_dotenv()

LLM="gemini-2.5-flash"

my_user_id = "adk_adventurer_001"

# Sports news agent
sports_news_agent = Agent(
    name="sports_news_agent",
    model=LLM,
    tools=[google_search],
    instruction="""You are news reporter with expertise in Sports.
    Your goal is to provide news related to international sports.
    When you provide the news list maximum of 5 articles and include highlights of each match.
    """,
    output_key="destination"
)


# Business news agent
business_news_agent = Agent(
    name="business_news_agent",
    model=LLM,
    tools=[google_search],
    instruction="""You are news reporter with expertise in Business.
    Your goal is to provide news related to business world.
    When you provide the news list maximum of 5 articles.
    """,
    output_key="destination"
)


# Business news agent
entertainment_news_agent = Agent(
    name="entertainment_news_agent",
    model=LLM,
    tools=[google_search],
    instruction="""You are news reporter with expertise in Entertainment.
    Your goal is to provide news related to movies and tv.
    When you provide the news list maximum of 5 articles.
    """,
    output_key="destination"
)


# Router agent to route to the correct expertise agent.
router_agent = Agent(
    name="router_agent",
    model=LLM,
    instruction="""
    You are a request router. Your job is to analyze a user's query and decide which of the following agents or workflows is best suited to handle it.
    Do not answer the query yourself, only return the name of the most appropriate choice.

    Available Options:
    - 'sports_news_agent': For queries *only* about Football
    - 'business_news_agent': For queries about *only* about Cricket.
    - 'entertainment_news_agent': For queries *only* about Football

    Only return the single, most appropriate option's name and nothing else.
    """
)


news_reporters = {
    "sports_news_agent": sports_news_agent,
    "business_news_agent": business_news_agent,
    "entertainment_news_agent": entertainment_news_agent
}


async def run_agent_query(agent: Agent, query: str, session: Session, user_id: str, is_router: bool = False):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"Running query for agent: '{agent.name}'")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=agent.name
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user")
        ):
            if not is_router:
                print("..")
            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if not is_router:
        print("\n" + "-" * 50)
        print("Agent Response:")
        print(final_response)
        print("-" * 50 + "\n")

    return final_response


session_service = InMemorySessionService()

async def main():
    """Main function to initiate the agent run."""
    router_session = None
    worker_session = None
    while True:
        try:
            query = input("\n\nUser query: ")
        except KeyboardInterrupt:
            print("\n\nExiting Sports Agent.. Bye!!")
            sys.exit(0)

        print("\n" + "=" * 60)
        print(f"Processing New Query: '{query}'")
        print("=" * 60)
        print("Router deciding on expert...")
        router_session = await session_service.create_session(app_name=router_agent.name, user_id=my_user_id)
        chosen_reporter = await run_agent_query(router_agent, query, router_session, my_user_id, is_router=True)
        chosen_reporter = chosen_reporter.strip().replace("'", "")
        print(f"Router has selected the expert: '{chosen_reporter}'")

        if chosen_reporter in news_reporters:
            news_reporter = news_reporters[chosen_reporter]
            print(f"--- Handing off to {news_reporter.name} ---")
            worker_session = await session_service.create_session(app_name=news_reporter.name, user_id=my_user_id)
            await run_agent_query(news_reporter, query, worker_session, my_user_id)
            print(f"--- {news_reporter.name} Complete ---")
        else:
            print("Error: Router could not find an expert to process your query")



asyncio.run(main())
