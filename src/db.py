import os
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


def init_db() -> None:
    """Create the SQL tables if they do not already exist.
        prime_parts: Stores information about prime parts
            - slug: Unique identifier for the item (Primary key)
            - name: Name of the item
            - ducats: Ducat value of the item (Default 0)
            - fetched_at: Timestamp of when the item was last fetched 

        price_snapshots: Stores price snapshots for prime parts
            - id: Unique identifier for the snapshot
            - slug: Foreign key referencing the prime_parts table
            - lowest_price: Lowest price of the item at the time of the snapshot
            - average_price: Average price of the item at the time of the snapshot
            - fetched_at: Timestamp of when the snapshot was taken
        collection_stats: Stores cumulative statistics about price collection attempts
            - id: Unique identifier for the stats (Primary key, always 1)
            - attempted_entries: Number of entries that were attempted to be collected
            - denied_entries: Number of entries that were denied
    """
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS prime_parts (
                slug TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                ducats INTEGER NOT NULL DEFAULT 0,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id BIGSERIAL PRIMARY KEY,
                slug TEXT NOT NULL REFERENCES prime_parts(slug),
                lowest_price NUMERIC(10, 2),
                average_price NUMERIC(10, 2) NOT NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        connection.execute(text("""
            ALTER TABLE price_snapshots
            ADD COLUMN IF NOT EXISTS lowest_price NUMERIC(10, 2)
        """))
        connection.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM pg_attribute
                    WHERE attrelid = 'price_snapshots'::regclass
                      AND attname = 'average_price'
                      AND NOT attnotnull
                ) THEN
                    DELETE FROM price_snapshots
                    WHERE average_price IS NULL;

                    ALTER TABLE price_snapshots
                    ALTER COLUMN average_price SET NOT NULL;
                END IF;
            END $$;
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS collection_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                attempted_entries BIGINT NOT NULL DEFAULT 0,
                denied_entries BIGINT NOT NULL DEFAULT 0
            )
        """))
        connection.execute(text("""
            INSERT INTO collection_stats (id)
            VALUES (1)
            ON CONFLICT (id) DO NOTHING
        """))


def save_prime_parts(prime_parts: Iterable[dict]) -> None:
    """Insert or update prime part information."""
    rows = []

    # Loop through the list of prime parts and prepare the data for insertion
    for item in prime_parts:
        slug = item.get("slug")
        if not slug:
            continue
        name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")
        ducats = int(item.get("ducats", 0) or 0)
        rows.append({"slug": slug, "name": name, "ducats": ducats})

    if not rows:
        return

    # Use a single transaction to insert or update all prime parts
    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO prime_parts (slug, name, ducats)
            VALUES (:slug, :name, :ducats)
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                ducats = EXCLUDED.ducats,
                fetched_at = CURRENT_TIMESTAMP
        """), rows)


def search_prime_parts(item: str):
    """Return prime parts whose name is item."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT name, slug, ducats, fetched_at
            FROM prime_parts
            WHERE name ILIKE :pattern
            ORDER BY name
        """), {"pattern": f"%{item}%"})
        return result.mappings().all()


def get_prime_parts(search: str = "", sort: str = "name", order: str = "asc",
                    limit: int = 50, offset: int = 0):
    """Return prime parts with their latest stored price snapshot."""
    sort_columns = {
        "name": "prime_parts.name",
        "ducats": "prime_parts.ducats",
        "price": "latest_prices.average_price",
        "updated": "latest_prices.fetched_at",
    }
    sort_column = sort_columns.get(sort, sort_columns["name"])
    sort_order = "DESC" if order.lower() == "desc" else "ASC"

    with engine.connect() as connection:
        result = connection.execute(text(f"""
            SELECT
                prime_parts.name,
                prime_parts.slug,
                prime_parts.ducats,
                COALESCE(latest_prices.lowest_price, latest_prices.average_price) AS lowest_price,
                latest_prices.average_price,
                latest_prices.fetched_at
            FROM prime_parts
            LEFT JOIN LATERAL (
                SELECT lowest_price, average_price, fetched_at
                FROM price_snapshots
                WHERE price_snapshots.slug = prime_parts.slug
                ORDER BY fetched_at DESC
                LIMIT 1
            ) AS latest_prices ON TRUE
            WHERE prime_parts.name ILIKE :pattern
            ORDER BY {sort_column} {sort_order} NULLS LAST, prime_parts.name ASC
            LIMIT :limit OFFSET :offset
        """), {
            "pattern": f"%{search}%",
            "limit": limit,
            "offset": offset,
        })
        return result.mappings().all()


def count_prime_parts(search: str = "") -> int:
    """Return the number of prime parts matching a search string."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT COUNT(*)
            FROM prime_parts
            WHERE name ILIKE :pattern
        """), {"pattern": f"%{search}%"})
        return result.scalar_one()


def get_prime_part(slug: str):
    """Return one prime part with its latest stored price snapshot."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                prime_parts.name,
                prime_parts.slug,
                prime_parts.ducats,
                COALESCE(latest_prices.lowest_price, latest_prices.average_price) AS lowest_price,
                latest_prices.average_price,
                latest_prices.fetched_at
            FROM prime_parts
            LEFT JOIN LATERAL (
                SELECT lowest_price, average_price, fetched_at
                FROM price_snapshots
                WHERE price_snapshots.slug = prime_parts.slug
                ORDER BY fetched_at DESC
                LIMIT 1
            ) AS latest_prices ON TRUE
            WHERE prime_parts.slug = :slug
        """), {"slug": slug})
        return result.mappings().one_or_none()


def get_latest_price_timestamp():
    """Return the timestamp of the newest stored price snapshot."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT MAX(fetched_at)
            FROM price_snapshots
        """))
        return result.scalar_one_or_none()


def get_top_ducat_parts(limit: int = 10):
    """Return the prime parts with the highest ducat values."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT name, slug, ducats
            FROM prime_parts
            ORDER BY ducats DESC, name ASC
            LIMIT :limit
        """), {"limit": limit})
        return result.mappings().all()


def save_price_snapshot(slug: str, lowest_price, average_price) -> bool:
    """Save one lowest-price and average-price observation for an item."""
    if average_price is None:
        return False

    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO price_snapshots (slug, lowest_price, average_price)
            VALUES (:slug, :lowest_price, :average_price)
        """), {
            "slug": slug,
            "lowest_price": lowest_price,
            "average_price": average_price,
        })
    return True


def record_collection_attempt(denied: bool) -> None:
    """Add one price lookup to the cumulative collection statistics."""
    with engine.begin() as connection:
        connection.execute(text("""
            UPDATE collection_stats
            SET attempted_entries = attempted_entries + 1,
                denied_entries = denied_entries + :denied
            WHERE id = 1
        """), {"denied": int(denied)})


def get_collection_stats():
    """Return cumulative attempted, denied, and denial-rate statistics."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                attempted_entries,
                denied_entries,
                CASE
                    WHEN attempted_entries = 0 THEN 0
                    ELSE denied_entries * 100.0 / attempted_entries
                END AS denial_rate
            FROM collection_stats
            WHERE id = 1
        """))
        return result.mappings().one()


def delete_old_snapshots(days: int = 90) -> None:
    """Delete price snapshots older than the specified number of days."""
    with engine.begin() as connection:
        connection.execute(text("""
            DELETE FROM price_snapshots
            WHERE fetched_at < CURRENT_TIMESTAMP - (:days * INTERVAL '1 day')
        """), {"days": days})


# Potential use to track how many of each ducat price there is
def get_ducat_stats():
    """Return summary statistics for stored ducat values."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                COUNT(*) AS item_count,
                AVG(ducats) AS average_ducats,
                MIN(ducats) AS min_ducats,
                MAX(ducats) AS max_ducats
            FROM prime_parts
        """))
        return result.mappings().one()


def get_hourly_price_trend(slug: str, days: int = 30):
    """Return hourly average price trend for one item."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                DATE_TRUNC('hour', fetched_at) AS hour_bucket,
                AVG(average_price) AS avg_price,
                MIN(average_price) AS min_price,
                MAX(average_price) AS max_price
            FROM price_snapshots
            WHERE slug = :slug
              AND fetched_at >= CURRENT_TIMESTAMP - (:days * INTERVAL '1 day') AND average_price IS NOT NULL
            GROUP BY DATE_TRUNC('hour', fetched_at)
            ORDER BY hour_bucket
        """), {"slug": slug, "days": days})
        return result.mappings().all()


def get_best_items_to_buy(days: int = 30, limit: int = 20):
    """Rank items by their recent average platinum cost per ducat."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                prime_parts.name,
                prime_parts.slug,
                prime_parts.ducats,
                AVG(price_snapshots.average_price) AS average_price,
                prime_parts.ducats / NULLIF(AVG(price_snapshots.average_price), 0) AS ducats_per_platinum,
                COUNT(price_snapshots.id) AS snapshot_count,
                MAX(price_snapshots.fetched_at) AS last_snapshot
            FROM price_snapshots
            JOIN prime_parts ON prime_parts.slug = price_snapshots.slug
            WHERE price_snapshots.fetched_at >= CURRENT_TIMESTAMP - (:days * INTERVAL '1 day')
              AND price_snapshots.average_price IS NOT NULL
              AND prime_parts.ducats > 0
            GROUP BY prime_parts.name, prime_parts.slug, prime_parts.ducats
            ORDER BY ducats_per_platinum DESC, average_price ASC
            LIMIT :limit
        """), {"days": days, "limit": limit})
        return result.mappings().all()


def get_best_market_hours(days: int = 30, min_items: int = 10):
    """Find recurring hours when the flat average platinum price is lowest."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            WITH recent_prices AS (
                SELECT
                    slug,
                    EXTRACT(HOUR FROM fetched_at)::INTEGER AS hour_of_day,
                    average_price
                FROM price_snapshots
                WHERE fetched_at >= CURRENT_TIMESTAMP - (:days * INTERVAL '1 day')
                  AND average_price IS NOT NULL
            ),
            item_baselines AS (
                SELECT slug, AVG(average_price) AS baseline_price
                FROM recent_prices
                GROUP BY slug
            ),
            hourly_item_prices AS (
                SELECT
                    slug,
                    hour_of_day,
                    AVG(average_price) AS hourly_price
                FROM recent_prices
                GROUP BY slug, hour_of_day
            )
            SELECT
                hourly_item_prices.hour_of_day,
                AVG(hourly_item_prices.hourly_price) AS average_price
            FROM hourly_item_prices
            JOIN item_baselines ON item_baselines.slug = hourly_item_prices.slug
            GROUP BY hourly_item_prices.hour_of_day
            HAVING COUNT(*) >= :min_items
            ORDER BY average_price ASC
        """), {"days": days, "min_items": min_items})
        return result.mappings().all()
