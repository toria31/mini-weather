import requests
import sys

# ---CONFIGURATION---
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


# Fetch the current weather data for a given city using OpenWeatherMap API
def get_weather_data(city_name, api_key):

    # Parameters for the API request
    params = {"q": city_name, "appid": api_key, "units": "metric"}

    try:

        # Check if the 'requests' library is installed
        if "requests" not in sys.modules:
            return {"error": "The 'requests' library is missing."}

        # Make the GET request to OpenWeatherMap API
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Parse the JSON response into the Python dictionary
        data = response.json()

        if data.get("cod") == "404":
            return {"error": f"City '{city_name}' not found."}

        # Extract the required data
        city = data.get("name", "N/A")
        country = data.get("sys", {}).get("country", "N/A")
        main_weather = data.get("main", {})
        weather_info = data.get("weather", [{}])[0]

        temp_celsius = main_weather.get("temp")
        description = weather_info.get("description", "N/A").capitalize()

        if temp_celsius is None:
            return {"error": "Incomplete data retrieved from API."}

        return {
            "city": city,
            "country": country,
            "temp": f"{temp_celsius:.1f}°C",
            "description": description,
        }

    # Handling common errors
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return {"error": "Invalid API Key."}
        return {"error": f"HTTP error {response.status_code}: {e}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
