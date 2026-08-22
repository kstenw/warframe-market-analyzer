import os
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


def init_db() -> None:
    """Create the PostgreSQL tables if they do not already exist."""
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
                lowest_price INTEGER,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))


def save_prime_parts(prime_parts: Iterable[dict]) -> None:
    """Insert or update prime-part information."""
    rows = []
    for item in prime_parts:
        slug = item.get("slug")
        if not slug:
            continue
        name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")
        ducats = int(item.get("ducats", 0) or 0)
        rows.append({"slug": slug, "name": name, "ducats": ducats})

    if not rows:
        return

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
    """Return prime parts whose name contain item."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT name, slug, ducats, fetched_at
            FROM prime_parts
            WHERE name ILIKE :pattern
            ORDER BY name
        """), {"pattern": f"%{item}%"})
        return result.mappings().all()


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


def save_price_snapshot(slug: str, lowest_price) -> None:
    """Save one lowest-price observation for an item."""
    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO price_snapshots (slug, lowest_price)
            VALUES (:slug, :lowest_price)
        """), {"slug": slug, "lowest_price": lowest_price})


def delete_old_snapshots(days: int = 90) -> None:
    """Delete price snapshots older than the specified number of days."""
    with engine.begin() as connection:
        connection.execute(text("""
            DELETE FROM price_snapshots
            WHERE fetched_at < CURRENT_TIMESTAMP - (:days * INTERVAL '1 day')
        """), {"days": days})


def get_lowest_prices():
    """Return the lowest recorded price for each prime part."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                prime_parts.name,
                prime_parts.slug,
                MIN(price_snapshots.lowest_price) AS lowest_price
            FROM price_snapshots
            JOIN prime_parts ON prime_parts.slug = price_snapshots.slug
            WHERE price_snapshots.lowest_price IS NOT NULL
            GROUP BY prime_parts.name, prime_parts.slug
            ORDER BY lowest_price ASC
        """))
        return result.mappings().all()


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
