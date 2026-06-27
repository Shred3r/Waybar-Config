#!/usr/bin/env python

import requests
import json
import sys

# Weather icons
weather_icons = {
    "sunny": "🔆",
    "cloudy": "",
    "rainy": "",
    "snowy": "❄",
    "fair": "🌤️", 
    "severe": "",
    "default": "",
}

# Location coordinates (Defaulted to Tucson, AZ)
# You can change these to any latitude/longitude
LATITUDE = 32.2226
LONGITUDE = -110.9747

# Open-Meteo API URLs
WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,visibility&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=auto"
AQI_URL = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LATITUDE}&longitude={LONGITUDE}&current=us_aqi"

def get_weather_status(wmo_code):
    """Maps standard WMO codes to your status phrases and icons."""
    if wmo_code == 0:
        return "Clear sky", "sunny", weather_icons["sunny"]
    elif wmo_code in [1, 2]:
        return "Mainly clear", "fair", weather_icons["fair"]
    elif wmo_code == 3:
        return "Overcast", "cloudy", weather_icons["cloudy"]
    elif wmo_code in [45, 48]:
        return "Fog", "cloudy", weather_icons["cloudy"]
    elif wmo_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return "Rainy", "rainy", weather_icons["rainy"]
    elif wmo_code in [71, 73, 75, 77, 85, 86]:
        return "Snowy", "snowy", weather_icons["snowy"]
    elif wmo_code in [95, 96, 99]:
        return "Thunderstorm", "severe", weather_icons["severe"]
    else:
        return "Unknown", "default", weather_icons["default"]

try:
    # Fetch weather and AQI data
    weather_resp = requests.get(WEATHER_URL)
    aqi_resp = requests.get(AQI_URL)
    
    weather_resp.raise_for_status()
    aqi_resp.raise_for_status()
    
    weather_data = weather_resp.json()
    aqi_data = aqi_resp.json()

    current = weather_data["current"]
    daily = weather_data["daily"]

    # Map current conditions
    temp = f"{round(current['temperature_2m'])}°F"
    temp_feel = f"Feels like {round(current['apparent_temperature'])}°F"
    
    status, status_class, icon = get_weather_status(current['weather_code'])
    
    wind_text = f"༄ {round(current['wind_speed_10m'])} MPH"
    humidity_text = f"  {current['relative_humidity_2m']}%"
    
    # Open-Meteo visibility is in meters; converting to miles
    vis_miles = round(current['visibility'] / 1609.34, 1)
    visibility_text = f"  {vis_miles} mi"

    # Air Quality
    air_quality_index = aqi_data["current"]["us_aqi"]

    # Min/Max temps (taking today's forecast at index 0)
    temp_max = f"{round(daily['temperature_2m_max'][0])}°F"
    temp_min = f"{round(daily['temperature_2m_min'][0])}°F"
    temp_min_max = f"  {temp_min}\t  {temp_max}"

    # Precipitation
    precip = current['precipitation']
    prediction = f"\n    {precip} in" if precip > 0 else ""

    # Build the tooltip
    tooltip_text = str.format(
        "{}\n{}\n{}\n\n{}\n{}\t{}\n{}\tAQI {}{}",
        f'<span size="xx-large">{temp}</span>',
        f"<big>{status}</big>",
        f"<small>{temp_feel}</small>",
        f"<big>{temp_min_max}</big>",
        wind_text, humidity_text,
        visibility_text, air_quality_index,
        prediction
    )

    # Output for Waybar
    out_data = {
        "text": f"<big>{icon}</big>  {temp}",
        "alt": status,
        "tooltip": tooltip_text,
        "class": status_class,
    }
    
    print(json.dumps(out_data))

except Exception as e:
    # Failsafe so Waybar doesn't crash on network loss
    error_data = {
        "text": "Disconnected",
        "alt": "Offline",
        "tooltip": f"Error fetching weather: {str(e)}",
        "class": "error"
    }
    print(json.dumps(error_data))
    sys.exit(1)
