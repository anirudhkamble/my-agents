import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph

load_dotenv()


LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0, 
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


class AgentState(TypedDict):
    query: str
    budget: str
    search_results: list[str]
    online_shopping_sites: list[str]


def list_devices(state: AgentState) -> AgentState:
    """This is a first node in the sequence which will find a products according to the query.    
    """
    print("\nSearching for you gadget..")
    messages = [
        SystemMessage(content="""
            You are a tech. reviewer. Your goal is find the best devices within given budget.
            You must only provide these details Phone brand, price and tech stats.
            Provide a maximun of 5 results in ascending order of their price.
        """),
        HumanMessage(content=f"Query: {state['query'], state['budget']}"),
    ]

    response = LLM.invoke(messages)
    state["search_results"] = response.content
    return state

def find_offers(state: AgentState) -> AgentState:
    """This is the second node of our sequence"""
    print("\nFinding best site to buy your gadget..")
    messages = [
        SystemMessage(content="""
            You are a an experienced shopper. 
            Your goal is provide the online sites where I can purchase the devices.
            Provide only the details: URL for buying these devices and the device information.
        """),
        HumanMessage(content=f"Query: {state['search_results'], state['budget']}"),
    ]

    response = LLM.invoke(messages)
    state["online_shopping_sites"] = response.content
    return state


def setup_agents():
    """This function creates the nodes and edges using langgraph"""
    graph = StateGraph(AgentState)
    graph.add_node("list_devices", list_devices)
    graph.add_node("find_offers", find_offers)
    graph.set_entry_point("list_devices")
    graph.add_edge("list_devices", "find_offers")
    graph.set_finish_point("find_offers")
    return graph.compile()


def main():
    app = setup_agents()
    print("\n" + "+" * 60)
    print("Electronics Shopper Agent...")
    print("+" * 60)
    while True:
        try:
            query = input("\nWhat electronics are you looking for?: ")
            budget = input("What is your budget?: ")
        except KeyboardInterrupt:
            print("Exiting Electronics Shopper Agent")
            sys.exit(0)

        result = app.invoke({"query": query, "budget": budget})

        print("\n" + "+" * 60)
        print("Results: ")
        print("+" * 60)
        for key, value in result.items():
            if key == "online_shopping_sites":
                print(value)


if __name__ == "__main__":
    main()
