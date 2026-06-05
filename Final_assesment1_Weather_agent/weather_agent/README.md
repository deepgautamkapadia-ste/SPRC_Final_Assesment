# Weather Agent

A small Python weather assistant that:

- asks for your name
- detects your approximate location from your IP address
- fetches the current weather for that location
- prints a personalized weather summary with local time, temperature, and conditions

## Features

- IP-based location lookup
- Current weather lookup from Open-Meteo
- Human-readable weather descriptions
- Temperature classification such as `cold`, `cool`, `comfortable`, `warm`, and `hot`
- Local time formatting using the detected UTC offset
- Friendly greeting based on day or night

## Project Structure

- `main.py` - command-line entry point
- `graph.py` - LangGraph workflow definition
- `components/config.py` - API endpoints, thresholds, and shared configuration
- `components/helper_functions.py` - time, greeting, and weather formatting helpers
- `components/nodes.py` - graph node implementations
- `components/state.py` - state schema for the agent
- `components/schema.py` - typed data models for API payloads
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.10+
- Internet connection

## Installation

1. Create and activate a virtual environment.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start the program from the project root:

```bash
python main.py
```

The program will prompt for your name. If you press Enter, it will default to `User`.

## How It Works

1. `main.py` creates the initial `WeatherAgentState`.
2. `graph.py` defines the workflow for the weather agent.
3. `components/nodes.py` contains the logic to:
   - resolve location data from IP-based geolocation services
   - fetch current weather from Open-Meteo
   - build the final human-readable weather message
4. The final weather report is printed to the console.

## Configuration

The project uses `pydantic-settings` and loads environment variables from `.env` if present.

You can adjust values in `components/config.py`, including:

- `LOCATION_API_URL`
- `WEATHER_API_BASE_URL`
- `REQUEST_TIMEOUT`
- temperature thresholds

## Example Output

```text
============================================================
WEATHER INFORMATION
============================================================
Time: 09:30 UTC | 15:00 (UTC+05:30)

Good morning, User!

Your current location: Mumbai, Maharashtra, India

Current weather conditions:
- Partly cloudy
- Temperature: 29.4C (warm)
- Wind: 13.2 km/h
```

## Troubleshooting

- If the program cannot reach the APIs, check your internet connection.
- If you see an error related to the LangGraph workflow, make sure the graph is compiled and that the weather-fetch step is connected in the workflow.
- If location lookup fails, the app will try multiple IP geolocation providers before giving up.

## Notes

- This project is designed as a command-line weather assistant.
- The output depends on live API responses, so values will change from run to run.
