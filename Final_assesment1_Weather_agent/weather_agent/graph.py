from langgraph.graph import StateGraph, START, END
from components.state import WeatherAgentState
from components.nodes import (
    fetch_location_data,
    fetch_weather_data, 
    generate_weather_info
)

builder = StateGraph(WeatherAgentState)

# Add nodes
builder.add_node("fetch_location_data", fetch_location_data)
builder.add_node("fetch_weather_data", fetch_weather_data)
builder.add_node("generate_weather_info", generate_weather_info)

# Add edges - simple linear flow
# Update: LangGraph processes nodes in parallel by default, so order doesn't matter
builder.add_edge(START, "fetch_location_data")
builder.add_edge("fetch_location_data", "generate_weather_info")
builder.add_edge("generate_weather_info", END)

# Auto-compile the graph
weather_agent = builder