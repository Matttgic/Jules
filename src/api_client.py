import requests
from decouple import config

API_KEY = config("API_KEY", default=None)
API_HOST = config("API_HOST", default="api-football-v1.p.rapidapi.com")

def make_api_request(endpoint, params=None):
    """
    Makes a request to the API-Football endpoint.

    Args:
        endpoint (str): The API endpoint to call (e.g., '/fixtures').
        params (dict, optional): A dictionary of query parameters. Defaults to None.

    Returns:
        dict: The JSON response from the API, or None if the request fails.
    """
    url = f"https://{API_HOST}/v3/{endpoint}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
