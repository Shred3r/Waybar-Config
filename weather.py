#!/usr/bin/env python

import subprocess
from pyquery import PyQuery  # install using `pip install pyquery`
import json

# weather icons
weather_icons = {
    "sunny": "🔆",
    #"clearNight": "☾",
    "cloudy": "",
    #"cloudyFoggyNight": "",
    "rainy": "",
    #"rainyNight": "",
    "snowy": "❄",
    #"snowyIcyNight": "",
    "fair": "🌤️", 
    "severe": "",
    "default": "",
}

# get location_id
# to get your own location_id, go to https://weather.com & search your location.
# once you choose your location, you can see the location_id in the URL(64 chars long hex string)

location_id = "4814d18dab305c056be0263beaefdbed8e5b5a486c3ca00d354df34df353fede"  

# priv_env_cmd = 'cat $PRIV_ENV_FILE | grep weather_location | cut -d "=" -f 2'
# location_id = subprocess.run(
#     priv_env_cmd, shell=True, capture_output=True).stdout.decode('utf8').strip()

# get html page
url = "https://weather.com/en-US/weather/today/l/" + location_id
html_data = PyQuery(url=url)
print(url)

# current temperature
temp = html_data("span[data-testid='TemperatureValue']").eq(0).text()
print(temp)

# current status phrase
status = html_data("div[data-testid='wxPhrase']").text()
status = (f"{status[:16]}.." if len(status) > 17 else status)
print(status)

status_Icon = status.split()[-1].lower()
print(status_Icon)

# status icon
icon = (
    weather_icons[status_Icon]
    if status_Icon in weather_icons
    else weather_icons["default"]
)
# print(icon)

# temperature feels like
temp_feel = html_data(
    "div[data-testid='FeelsLikeSection'] > span > span[data-testid='TemperatureValue']"
).text()

temp_feel_text = f"Feels like {temp_feel}f"
# print(temp_feel_text)

# min-max temperature
temp_min = (
    html_data("div[data-testid='wxData'] > span[data-testid='TemperatureValue']")
    .eq(1)
    .text()
)

temp_max = (
    html_data("div[data-testid='wxData'] > span[data-testid='TemperatureValue']")
    .eq(0)
    .text()
)

#CAN WRITE AN IF STATEMENT TO MANUALLY IDENTIFY HIGH AFTER EACH TIME THIS IS RAN,
#IN THE MEANTIME THIS IS BROKEN UNLESS THE WEBSITE UPDATES A HIGH
temp_min_max = f"  {temp_min}\t  {temp_max}"
# print(temp_min_max)

# wind speed
wind_speed = html_data("span[data-testid='Wind'] > span").eq(1).text()
wind_text = f"༄ {wind_speed} MPH"
print(wind_text)

# humidity
humidity = html_data("span[data-testid='PercentageValue']").eq(1).text()
humidity_text = f"  {humidity}"
# print(humidity_text)

# visibility
visbility = html_data("span[data-testid='VisibilityValue']").text()
visbility_text = f"  {visbility}"
# print(visbility_text)

# air quality index
air_quality_index = html_data("text[data-testid='DonutChartValue']").text()
# print(air_quality_index)

# hourly rain prediction
prediction = html_data("[data-testid='Precip']").text()
prediction = prediction.replace("Rain drop", "").split()[:5]
print(prediction)
seperator = ', '
prediction = seperator.join(prediction)
prediction = f"\n    {prediction}" if len(prediction) > 0 else prediction
print(prediction)

# tooltip text
tooltip_text = str.format(
    "{}\n{}\n{}\n\n{}\n{}\n{}\n{}",
    f'<span size="xx-large">{temp}</span>',
    f"<big>{status}</big>",
    f"<small>{temp_feel_text}</small>",
    f"<big>{temp_min_max}</big>",
    f"{wind_text}\t{humidity_text}",
    f"{visbility_text}\tAQI {air_quality_index}",
    f"<i>{prediction}</i>",
)

# print waybar module data
out_data = {
    "text": f"<big>{icon}</big>  {temp}",
    "alt": status,
    "tooltip": tooltip_text,
    "class": status_Icon,
}
print(json.dumps(out_data))
