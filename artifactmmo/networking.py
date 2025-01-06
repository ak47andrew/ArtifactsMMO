import aiohttp
from typing import Any
from os import getenv

BASE_URL = "https://api.artifactsmmo.com"


JSON_TYPE = dict[str, Any]


async def make_request(uri: str, method: str = "GET", **data: JSON_TYPE) -> JSON_TYPE:
    """
    Make an asynchronous HTTP request to the Artifacts MMO API.

    Parameters:
    - uri (str): The API endpoint URI.
    - method (str): The HTTP method for the request. Default is "GET".
    - **data (JSON_TYPE): Additional data to send with the request as json body.

    Returns:
    - JSON_TYPE: The JSON response data from the API.

    Raises:
    - aiohttp.ClientResponseError: If the HTTP request returns a 4xx or 5xx status code.

    Example:
    >>> response = await make_request("/", method="GET")
    >>> print(response)
    {<They all so f$%*ing long and boring, so... check out docs for yourself: https://api.artifactsmmo.com/docs/#/>}
    """
    headers = {
        "Authorization": f"Bearer {getenv('ARTIFACTS_MMO_TOKEN')}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.request(method, f"{BASE_URL}{uri}", headers=headers, json=data) as response:
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return (await response.json())["data"]
