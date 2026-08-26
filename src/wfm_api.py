from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    import aiohttp

API_BASE_URL = "https://api.warframe.market/v2"

# Standard headers for V2 API requests
HEADERS = {
    "accept": "application/json",
    "Platform": "pc",
    "Language": "en",
    "User-Agent": "python-requests/2.32.0"
}

def get_prime_parts_list():
    """Fetch the list of all prime parts from the API."""
    endpoint = f"{API_BASE_URL}/items"

    try:
        # Make a GET request to the API endpoint
        response = requests.get(endpoint, headers=HEADERS, timeout=15)
        response.raise_for_status()
        json_response = response.json()
        full_items_list = json_response.get('data', [])

        # Filter the list to include only prime parts
        prime_parts = []
        for item in full_items_list:
            item_name = item.get('i18n', {}).get('en', {}).get('name', '')
            ducat_value = item.get('ducats')
            is_prime_part = (
                'Prime' in item_name
                and 'Primed' not in item_name
                and 'Set' not in item_name
                and ducat_value is not None
            )
            if is_prime_part:
                prime_parts.append(item)
        return prime_parts

    except requests.exceptions.RequestException as e:
        return None
    
    except json.JSONDecodeError:
        return None


def get_average_price_top_4(slug: str):
    """Return the average platinum price of the four cheapest in-game orders."""
    endpoint = f"{API_BASE_URL}/orders/item/{slug}/top"

    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=10)
        response.raise_for_status()

        # Extract the relevant data from the JSON response
        json_response = response.json()
        sell_orders = json_response.get('data', {}).get('sell', [])
        ingame_orders = [
            order for order in sell_orders
            if order.get('user', {}).get('status') == 'ingame'
        ]

        # Sort the prices of the in-game orders and calculate the average of the four cheapest
        prices = sorted(
            order['platinum']
            for order in ingame_orders
            if 'platinum' in order
        )

        if not prices:
            return None

        cheapest_four = prices[:4]
        return round(sum(cheapest_four) / len(cheapest_four), 2)

    except requests.exceptions.RequestException:
        return None

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


async def get_average_price_top_4_async(
    session: aiohttp.ClientSession, slug: str
):
    """Asynchronously return the average price of the four cheapest orders."""
    import aiohttp

    endpoint = f"{API_BASE_URL}/orders/item/{slug}/top"

    try:
        async with session.get(endpoint, headers=HEADERS) as response:
            response.raise_for_status()
            # The API may return JSON with a non-JSON content type.
            json_response = json.loads(await response.text())

        sell_orders = json_response.get("data", {}).get("sell", [])
        ingame_orders = [
            order for order in sell_orders
            if order.get("user", {}).get("status") == "ingame"
        ]
        prices = sorted(
            order["platinum"]
            for order in ingame_orders
            if "platinum" in order
        )

        if not prices:
            return None

        cheapest_four = prices[:4]
        return round(sum(cheapest_four) / len(cheapest_four), 2)

    except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError,
            KeyError, TypeError, ValueError):
        return None

def get_price(slug: str):
    """Return the average platinum price of the four cheapest in-game orders."""
    return get_average_price_top_4(slug)
