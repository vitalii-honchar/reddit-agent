import os
import random
from typing import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

load_dotenv()


class GraphState(TypedDict):
    city: str
    human_query: str
    result: str


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


class WeatherResponse(BaseModel):
    conditions: str = Field(
        description="Weather conditions in the specified city",
    )


def select_random_city(state: GraphState) -> GraphState:
    """Select a random city and update graph state."""
    cities = ["San Francisco", "New York", "London", "Tokyo", "Sydney", "Paris", "Berlin"]
    selected_city = random.choice(cities)
    print(f"🎲 Randomly selected city: {selected_city}")
    
    return {
        "city": selected_city,
        "human_query": state.get("human_query", "What is the weather like?"),
        "result": ""
    }


def react_weather_agent(state: GraphState) -> GraphState:
    """Execute React agent for weather query."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    agent = create_react_agent(
        model=llm,
        tools=[get_weather],
        response_format=WeatherResponse,
        prompt=SystemMessage("You are a helpful weather assistant"),
    )
    
    # Create query with selected city
    query = f"What is the weather in {state['city']}?"
    messages = [HumanMessage(query)]
    
    print(f"🤖 Querying React agent: {query}")
    response = agent.invoke({"messages": messages})
    
    return {
        "city": state["city"],
        "human_query": state["human_query"],
        "result": response["structured_response"].conditions
    }


def print_result(state: GraphState) -> GraphState:
    """Print the final result to stdout."""
    print(f"\n📍 City: {state['city']}")
    print(f"🌤️  Weather: {state['result']}")
    print("=" * 50)
    return state


def create_weather_graph():
    """Create the LangGraph workflow."""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("select_city", select_random_city)
    workflow.add_node("react_agent", react_weather_agent)
    workflow.add_node("print_result", print_result)
    
    # Add edges
    workflow.add_edge(START, "select_city")
    workflow.add_edge("select_city", "react_agent")
    workflow.add_edge("react_agent", "print_result")
    workflow.add_edge("print_result", END)
    
    return workflow.compile()


def main():
    print("Weather Agent with LangGraph + React Agent")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY environment variable")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Create and run the graph
    graph = create_weather_graph()
    
    initial_state = {
        "city": "",
        "human_query": "What is the weather like?",
        "result": ""
    }
    
    print("🚀 Starting weather agent workflow...\n")
    graph.invoke(initial_state)
    
    print("\n✅ Workflow completed!")


if __name__ == "__main__":
    main()
