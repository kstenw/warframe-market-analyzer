import asyncio
import time

import aiohttp

import db
import wfm_api


REQUEST_DELAY = 0.4
COLLECTION_INTERVAL = 30 * 60
SNAPSHOT_RETENTION_DAYS = 90


async def collect_prices():
    """Fetch and store one price snapshot for every prime part asynchronously."""
    collection_start = time.perf_counter()
    prime_parts = wfm_api.get_prime_parts_list()

    if prime_parts is None:
        print("Could not fetch prime parts.")
        return

    db.init_db()
    db.save_prime_parts(prime_parts)

    items = [item for item in prime_parts if item.get("slug")]
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def fetch_item(number, item):
            # Space request starts to stay below the API rate limit.
            await asyncio.sleep((number - 1) * REQUEST_DELAY)
            price = await wfm_api.get_average_price_top_4_async(
                session, item["slug"]
            )
            return number, item, price

        tasks = [
            asyncio.create_task(fetch_item(number, item))
            for number, item in enumerate(items, start=1)
        ]
        attempted = len(tasks)
        denied = 0

        for completed in asyncio.as_completed(tasks):
            number, item, average_price = await completed
            saved = db.save_price_snapshot(item["slug"], average_price)
            if not saved:
                denied += 1
            db.record_collection_attempt(not saved)

            name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")
            print(
                f"{number}/{len(prime_parts)}: {name} = "
                f"{average_price} platinum"
            )

    # Delete old snapshots after 90 days to keep the database size manageable
    db.delete_old_snapshots(SNAPSHOT_RETENTION_DAYS)
    denial_rate = (denied / attempted * 100) if attempted else 0
    elapsed_seconds = time.perf_counter() - collection_start
    entries_per_second = attempted / elapsed_seconds if elapsed_seconds else 0
    print(
        f"Price collection complete. Denied {denied}/{attempted} entries "
        f"({denial_rate:.2f}%) in {elapsed_seconds:.2f} seconds."
    )
    print(f"Effective rate: {entries_per_second:.2f} entries/second.")
    stats = db.get_collection_stats()
    print(
        f"Cumulative: denied {stats['denied_entries']}/"
        f"{stats['attempted_entries']} entries "
        f"({float(stats['denial_rate']):.2f}%)."
    )


async def run_forever():
    """Collect prices repeatedly every 30 minutes."""
    while True:
        try:
            await collect_prices()
        except Exception as error:
            print(f"Collection failed: {error}")

        print(f"Waiting {COLLECTION_INTERVAL // 60} minutes...")
        await asyncio.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_forever())
