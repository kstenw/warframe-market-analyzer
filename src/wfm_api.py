from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import requests
import pandas as pd

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
        return calculate_clean_average(sell_orders)

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
        return calculate_clean_average(sell_orders)

    except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError,
            KeyError, TypeError, ValueError):
        return None


def calculate_clean_average(sell_orders):
    """Average up to four cheapest valid prices after removing IQR outliers."""
    prices = pd.DataFrame([
        {
            "price": order.get("platinum"),
            "status": order.get("user", {}).get("status"),
        }
        for order in sell_orders
    ])

    if prices.empty:
        return None

    prices["price"] = pd.to_numeric(prices["price"], errors="coerce")
    prices = prices[
        (prices["status"] == "ingame")
        & prices["price"].notna()
        & (prices["price"] > 0)
    ]

    if prices.empty:
        return None

    first_quartile = prices["price"].quantile(0.25)
    third_quartile = prices["price"].quantile(0.75)
    interquartile_range = third_quartile - first_quartile
    lower_bound = first_quartile - 1.5 * interquartile_range
    upper_bound = third_quartile + 1.5 * interquartile_range
    clean_prices = prices[
        prices["price"].between(lower_bound, upper_bound)
    ]["price"]

    if clean_prices.empty:
        return None

    return round(clean_prices.nsmallest(4).mean(), 2)

def get_price(slug: str):
    """Return the average platinum price of the four cheapest in-game orders."""
    return get_average_price_top_4(slug)
