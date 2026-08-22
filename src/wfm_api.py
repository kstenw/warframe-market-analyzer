import requests
import json

API_BASE_URL = "https://api.warframe.market/v2"

# Standard headers for V2 API requests
HEADERS = {
    "accept": "application/json",
    "Platform": "pc",
    "Language": "en"
}

def get_prime_parts_list():
    """Fetch the list of all prime parts from the API."""
    endpoint = f"{API_BASE_URL}/items"

    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=15)
        response.raise_for_status()
        json_response = response.json()
        full_items_list = json_response.get('data', [])

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


def get_lowest_price(slug: str):
    """Return the lowest current in-game sell price for an item."""
    endpoint = f"{API_BASE_URL}/orders/item/{slug}/top"

    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=10)
        response.raise_for_status()

        json_response = response.json()
        sell_orders = json_response.get('data', {}).get('sell', [])
        ingame_orders = [
            order for order in sell_orders
            if order.get('user', {}).get('status') == 'ingame'
        ]

        prices = [
            order['platinum']
            for order in ingame_orders
            if 'platinum' in order
        ]
        return min(prices) if prices else None

    except requests.exceptions.RequestException:
        return None

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None

def get_price(slug: str):
    """Calculate the average price of slug's top 5 ingame cheapest sell orders."""
    endpoint = f"{API_BASE_URL}/orders/item/{slug}/top"

    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=10)
        response.raise_for_status()

        json_response = response.json()
        top_sell_orders = json_response.get('data', {}).get('sell', [])
        
        # Filter for only ingame users
        ingame_orders = [order for order in top_sell_orders if order.get('user', {}).get('status') == 'ingame']

        if not ingame_orders:
            return 0
        
        average_price = sum([order['platinum'] for order in ingame_orders]) / len(ingame_orders)
        return int(average_price)
    
    except requests.exceptions.RequestException as e:
        return None
    
    except json.JSONDecodeError:
        return None
