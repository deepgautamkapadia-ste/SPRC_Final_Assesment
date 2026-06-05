from datetime import datetime, timezone, timedelta
from components.config import config

def classify_temperature(temp_celsius: float) -> str:
    """
    Classify temperature into human-readable categories.
    
    Args:
        temp_celsius: Temperature in Celsius
        
    Returns:
        Temperature classification string
    """
    if temp_celsius < config.TEMP_COLD:
        return "cold"
    elif temp_celsius < config.TEMP_COOL:
        return "cool"
    elif temp_celsius < config.TEMP_COMFORTABLE:
        return "comfortable"
    elif temp_celsius < config.TEMP_WARM:
        return "warm"
    else:
        return "hot"

def get_weather_description(weather_code: int) -> str:
    """
    Get human-readable weather description from WMO code.
    
    Args:
        weather_code: WMO weather code
        
    Returns:
        Weather description string
    """
    return config.WEATHER_CODE_DESCRIPTIONS.get(weather_code, f"Weather code {weather_code}")

def get_greeting(is_day: int) -> str:
    """
    Get appropriate greeting based on time of day.
    
    Args:
        is_day: 1 if day, 0 if night
        
    Returns:
        Greeting string
    """
    if bool(is_day):
        return "Good morning"
    else:
        return "Good evening"

def parse_utc_offset(utc_offset_str: str) -> timedelta:
    """
    Parse UTC offset string to timedelta object.
    
    Args:
        utc_offset_str: UTC offset in format '+05:30' or '-08:00'
        
    Returns:
        timedelta object representing the offset
    """
    try:
        # Remove '+' if present and split by ':'
        offset_str = utc_offset_str.replace('+', '')
        sign = -1 if offset_str.startswith('-') else 1
        offset_str = offset_str.replace('-', '')
        
        if ':' in offset_str:
            hours, minutes = map(int, offset_str.split(':'))
        else:
            # Handle cases like '+0530' without colon
            if len(offset_str) == 4:
                hours = int(offset_str[:2])
                minutes = int(offset_str[2:])
            else:
                hours = int(offset_str)
                minutes = 0
        
        return timedelta(hours=sign * hours, minutes=sign * minutes)
    except (ValueError, IndexError):
        # Default to UTC if parsing fails
        return timedelta(0)

def format_local_time(utc_time_str: str, utc_offset_str: str) -> str:
    """
    Convert UTC time to local time with timezone info.
    
    Args:
        utc_time_str: UTC time in ISO8601 format
        utc_offset_str: UTC offset string
        
    Returns:
        Formatted local time string
    """
    try:
        # Parse UTC time
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        
        # Calculate local time
        offset = parse_utc_offset(utc_offset_str)
        local_time = utc_time + offset
        
        # Format times
        utc_formatted = utc_time.strftime("%H:%M UTC")
        local_formatted = local_time.strftime("%H:%M")
        
        return f"{utc_formatted} | {local_formatted} (UTC{utc_offset_str})"
    except Exception:
        return "Time unavailable"
