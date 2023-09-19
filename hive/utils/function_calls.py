from duckduckgo_search import DDGS
import random
from hive.config.shared_config import SharedConfig

import os


def search_ddg(query: str) -> list:
    """
    Searches DuckDuckGo for the provided query and writes the results to a text file in the specified directory.
    @param query: The search query
    @return: A list of search results
    """
    output_directory = "D:/python/Quantum_HiveMind/hive/search_results"

    with DDGS() as ddgs:
        results = []
        for r in ddgs.text(query):
            results.append(r)

        # Create the full path to the output file
        output_file_path = os.path.join(output_directory, 'search_results.txt')

        with open(output_file_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write("%s\n" % result)

    return results


def get_current_weather(location: str = None, country: str = None) -> str:
    """
    Gets the current weather information
    @param location: The location for which to get the weather
    @param country: The ISO 3166-1 alpha-2 country code
    """

    # List of possible locations and countries
    locations = ['New York', 'Paris', 'Tokyo', 'Sydney', 'Cape Town']
    countries = ['US', 'FR', 'JP', 'AU', 'ZA']

    # If no location or country is provided, pick a random one
    if location is None:
        location = random.choice(locations)
    if country is None:
        country = random.choice(countries)

    if country == "FR":
        return f"The weather in {location}, {country} is terrible, as always"
    elif location == "California":
        return f"The weather in {location}, {country} is nice and sunny"
    else:
        return f"It's rainy and windy in {location}, {country}"


def recommend_youtube_channel() -> str:
    """
    Gets a really good recommendation for a YouTube channel to watch
    """
    return "Code-bullet"


def calculate_str_length(string: str) -> str:
    """
    Calculates the length of a string
    """
    return str(len(string))


def say_hello(greeting: str = "Hello, world!") -> str:
    """
    Returns a greeting message
    @param greeting: The greeting message to return
    """
    print("I activated the function!")

    return greeting


# Update SharedConfig
shared_config = SharedConfig()
shared_config.update_func_dict({
    'search_ddg': search_ddg,
    'get_current_weather': get_current_weather,
    'recommend_youtube_channel': recommend_youtube_channel,
    'calculate_str_length': calculate_str_length,
    'say_hello': say_hello
})


