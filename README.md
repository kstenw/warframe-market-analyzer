# Warframe Market Analyzer

Warframe Market Analyzer fetches Prime part data and market prices from the Warframe Market API. It stores item information, including platinum and ducat price, and historical price snapshots in PostgreSQL so the data can be queried later.

## Features

- Fetches Prime parts from the Warframe Market API.
- Stores item names, slugs, and ducat values in PostgreSQL.
- Fetches the lowest current in-game platinum sell price.
- Stores historical price snapshots for the last 90 days.
- Provides an interactive command-line lookup.
- Collects prices automatically every 30 minutes.

## Requirements

- Python 3.10 or newer
- PostgreSQL

The application creates the `prime_parts` and `price_snapshots` tables automatically when it starts.

## Run the Interactive App

From the project root:

```powershell
cd src
python main.py
```

The app fetches Prime parts, saves them to PostgreSQL, displays the first 20 API results, and asks for an item name. It then displays the item’s ducat value and average market price from the top in-game sell orders.

## Run Automatic Price Collection

From the project root:

```powershell
cd src
python collector.py
```

The collector fetches Prime parts, requests each item’s lowest in-game platinum price, saves each result in `price_snapshots`, and repeats every 30 minutes. It waits `0.4` seconds between requests, targeting 2.5 requests per second and staying below a 3-request-per-second limit.

Keep the collector process running on an always-on computer or server. Stop it with `Ctrl+C`.

To run one collection cycle without repeating:

```powershell
cd src
python -c "import collector; collector.collect_prices()"
```

## Database Tables

### `prime_parts`

Stores one current record for each item: `slug`, `name`, `ducats`, and `fetched_at`.

### `price_snapshots`

Stores historical observations: `id`, `slug`, `lowest_price`, and `fetched_at`.

Snapshots older than 90 days are deleted after each completed collection cycle. The `prime_parts` metadata is kept.
