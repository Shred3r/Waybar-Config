#!/usr/bin/env python

import subprocess
from pyquery import PyQuery  # install using `pip install pyquery`
import json

# weather icons
weather_icons = {
    "sunnyDay": "☀︎",
    "clearNight": "☾",
    "cloudyFoggyDay": "",
    "cloudyFoggyNight": "",
    "rainyDay": "",
    "rainyNight": "",
    "snowyIcyDay": "",
    "snowyIcyNight": "",
    "severe": "",
    "default": "",
}

# get location_id
# to get your own location_id, go to https://weather.com & search your location.
# once you choose your location, you can see the location_id in the URL(64 chars long hex string)
# like this: https://weather.com/en-IN/weather/today/l/c3e96d6cc4965fc54f88296b54449571c4107c73b9638c16aafc83575b4ddf2e
location_id = "813484e1eedc397652ea9ba6bf441f3a70394bd52e3b76ea27e71b7487fa11d9"  # TODO
# location_id = "8139363e05edb302e2d8be35101e400084eadcecdfce5507e77d832ac0fa57ae"

# priv_env_cmd = 'cat $PRIV_ENV_FILE | grep weather_location | cut -d "=" -f 2'
# location_id = subprocess.run(
#     priv_env_cmd, shell=True, capture_output=True).stdout.decode('utf8').strip()

# get html page
url = "https://weather.com/en-IN/weather/today/l/" + location_id
html_data = PyQuery(url=url)

# current temperature
temp = html_data("span[data-testid='TemperatureValue']").eq(0).text()
FTemp = float(temp[:len(temp)-1]) * (9/5) + 32
temp = str(int(FTemp)) + "°"

# current status phrase
status = html_data("div[data-testid='wxPhrase']").text()
status = f"{status[:16]}.." if len(status) > 17 else status
# print(status)

# status code
status_code = html_data("#regionHeader").attr("class").split(" ")[2].split("-")[2]
# print(status_code)

# status icon
icon = (
    weather_icons[status_code]
    if status_code in weather_icons
    else weather_icons["default"]
)
# print(icon)

# temperature feels like
temp_feel = html_data(
    "div[data-testid='FeelsLikeSection'] > span > span[data-testid='TemperatureValue']"
).text()

ftemp_feel = float(temp_feel[:len(temp_feel)-1]) * (9/5) + 32
ftemp_feel = str(int(ftemp_feel)) + "°"

temp_feel_text = f"Feels like {ftemp_feel}f"
# print(temp_feel_text)

# min-max temperature
temp_min = (
    html_data("div[data-testid='wxData'] > span[data-testid='TemperatureValue']")
    .eq(1)
    .text()
)
ftemp_min = float(temp_min[:len(temp_min)-1]) * (9/5) + 32
ftemp_min = str(int(ftemp_min)) + "°"

temp_max = (
    html_data("div[data-testid='wxData'] > span[data-testid='TemperatureValue']")
    .eq(0)
    .text()
)

#CAN WRITE AN IF STATEMENT TO MANUALLY IDENTIFY HIGH AFTER EACH TIME THIS IS RAN,
#IN THE MEANTIME THIS IS BROKEN UNLESS THE WEBSITE UPDATES A HIGH
try:    
    ftemp_max = float(temp_max[:len(temp_max)-1]) * (9/5) + 32
    ftemp_max = str(int(ftemp_max)) + "°"
except:
    ftemp_max = temp_max

temp_min_max = f"  {ftemp_min}\t  {ftemp_max}"
# print(temp_min_max)

# wind speed
wind_speed = html_data("span[data-testid='Wind']").text().split("\n")[0]
wind_text = f"༄ {wind_speed}"
print(wind_text)

# humidity
humidity = html_data("span[data-testid='PercentageValue']").text()
humidity_text = f"  {humidity}"
print(humidity_text)

# visibility
visbility = html_data("span[data-testid='VisibilityValue']").text()
visbility_text = f"  {visbility}"
# print(visbility_text)

# air quality index
air_quality_index = html_data("text[data-testid='DonutChartValue']").text()
# print(air_quality_index)

# hourly rain prediction
prediction = html_data("section[aria-label='Hourly Forecast']")(
    "div[data-testid='SegmentPrecipPercentage'] > span"
).text()
prediction = prediction.replace("Rain drop Chance of Rain", "")
prediction = f"\n\n    (hourly) {prediction}" if len(prediction) > 0 else prediction
# print(prediction)

# tooltip text
tooltip_text = str.format(
    "\t\t{}\t\t\n{}\n{}\n{}\n\n{}\n{}\n{}{}",
    f'<span size="xx-large">{temp}</span>',
    f"<big>{icon}</big>",
    f"<big>{status}</big>",
    f"<small>{temp_feel_text}</small>",
    f"<big>{temp_min_max}</big>",
    f"{wind_text}\t{humidity_text}",
    f"{visbility_text}\tAQI {air_quality_index}",
    f"<i>{prediction}</i>",
)

# print waybar module data
out_data = {
    "text": f"{icon} {temp}",
    "alt": status,
    "tooltip": tooltip_text,
    "class": status_code,
}
print(json.dumps(out_data))
