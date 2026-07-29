from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from tavily import TavilyClient
from datetime import datetime
from config import Config
from scholarly import scholarly
import requests
import geocoder

search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """Search the internet for general health info, historical medical background."""
    result = search.run(query)
    return result


@tool
def web_search_tavily(query: str, depth: str = "basic", max_results: int = 2) -> str:
    """Search for latest WHO/CDC guidelines, breaking health news, recently updated recommendations."""
    client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    response = client.search(query=query, search_depth=depth, max_results=max_results)
    results = response.get("results", [])
    if not results:
        return "No results found."
    return "\n\n".join(r.get("content", "")[:] for r in results[:2])


@tool
def get_datetime(query: str = "") -> str:
    """Get the current date and time for seasonal or time-sensitive health queries."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def get_user_location(query: str = "") -> str:
    """Get user's current location for region-specific health queries."""
    try:
        # More accurate than ipinfo
        g = geocoder.ip('me')
        return f"City: {g.city}, State: {g.state}, Country: {g.country}"
    except:
        return "Location unavailable"

@tool
def get_weather(city: str = "Guntur", country: str = "India") -> str:
    """Get current weather for health-related queries like heatstroke,
    seasonal allergies, humidity-related illness, cold weather precautions.
    city: Name of the city
    country: Name of the country
    """
    try:
        API_KEY = Config.OPENWEATHER_API_KEY

        # Step 1: Current Weather
        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city},{country}&appid={API_KEY}&units=metric"
        )
        weather = requests.get(weather_url).json()

        if str(weather.get("cod")) != "200":
            return f"City not found: {weather.get('message', 'Unknown error')}"

        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        # Step 2: AQI (free tier supports this)
        aqi_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
        )
        aqi_res = requests.get(aqi_url).json()
        aqi_index = aqi_res["list"][0]["main"]["aqi"]
        aqi_level = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        return (
            f"City: {weather['name']}, {country} | "
            f"Temp: {weather['main']['temp']}°C | "
            f"Feels Like: {weather['main']['feels_like']}°C | "
            f"Humidity: {weather['main']['humidity']}% | "
            f"Condition: {weather['weather'][0]['description'].title()} | "
            f"Wind: {weather['wind']['speed']} m/s | "
            f"AQI: {aqi_level.get(aqi_index, 'Unknown')}"
        )

    except Exception as e:
        return f"Weather unavailable: {str(e)}"

        
@tool
def google_scholar_search(query: str, max_results: int = 1) -> str:
    """Search Google Scholar for peer-reviewed health research and statistics."""
    results = []
    search_results = scholarly.search_pubs(query)
    for i, paper in enumerate(search_results):
        if i >= max_results:
            break
        results.append({
            "title": paper["bib"].get("title", ""),
            "year": paper["bib"].get("pub_year", ""),
            "abstract": paper["bib"].get("abstract", "")[:200]
        })
    if not results:
        return "No results found."
    r = results[0]
    return f"{r['title']} ({r['year']}): {r['abstract']}"


tools_list = [google_scholar_search, web_search_tavily, web_search, get_datetime,get_user_location,get_weather]