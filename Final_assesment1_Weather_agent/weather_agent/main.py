from graph import weather_agent
from components.state import WeatherAgentState

def main():
    try:
        name = input("Enter your name: ").strip()
    except EOFError:
        name = ""

    if not name:
        name = "User"
    
    state = WeatherAgentState(
        name=name,
        location_data=None,
        weather_data=None,
        weather_info=None
    )

    try:
        final_state = weather_agent.invoke(state)
        
        print("\n" + "=" * 60)
        print("WEATHER INFORMATION")
        print("=" * 60)
        
        if final_state.get("weather_info"):
            print(final_state["weather_info"])
        else:
            print("Sorry, unable to retrieve weather information at this time.")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
