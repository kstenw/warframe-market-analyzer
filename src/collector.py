import time

import db
import wfm_api


REQUEST_DELAY = 0.4
COLLECTION_INTERVAL = 30 * 60
SNAPSHOT_RETENTION_DAYS = 90


def collect_prices():
    """Fetch and store one price snapshot for every prime part."""
    prime_parts = wfm_api.get_prime_parts_list()

    if prime_parts is None:
        print("Could not fetch prime parts.")
        return

    db.init_db()
    db.save_prime_parts(prime_parts)

    print(f"Collecting prices for {len(prime_parts)} items...")

    for number, item in enumerate(prime_parts, start=1):
        slug = item.get("slug")
        name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")

        if not slug:
            continue

        average_price = wfm_api.get_average_price_top_4(slug)
        db.save_price_snapshot(slug, average_price)

        print(f"{number}/{len(prime_parts)}: {name} = {average_price} platinum")
        time.sleep(REQUEST_DELAY)

    db.delete_old_snapshots(SNAPSHOT_RETENTION_DAYS)
    print("Price collection complete.")


def run_forever():
    """Collect prices repeatedly every 30 minutes."""
    while True:
        try:
            collect_prices()
        except Exception as error:
            print(f"Collection failed: {error}")

        print(f"Waiting {COLLECTION_INTERVAL // 60} minutes...")
        time.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    run_forever()
