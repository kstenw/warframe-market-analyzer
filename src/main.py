import wfm_api
import db

def run_duckums():
    # Fetch the list of prime parts from the API
    prime_parts = wfm_api.get_prime_parts_list()
    if prime_parts is None:
        print("Could not fetch prime parts list from the API")
        return

    # Initialize the database and save the prime parts
    db.init_db()
    db.save_prime_parts(prime_parts)
    best_hours = db.get_best_market_hours()

    print("\n--------- Best Market Hours ---------")
    if not best_hours:
        print("No price snapshots available for the last 30 days.")
        print("Run collector.py first, then try main.py again.")
    else:
        for hour in best_hours[:5]:
            print(
                f"{int(hour['hour_of_day']):02d}:00 "
                f"- average price: {float(hour['average_price']):.2f} platinum"
            )
    print("-------------------------------------\n")
    
    # Loop through the first 20 items in the list
    print("\n-------------------------------------")
    for item in prime_parts[:20]:
        # Safely get the name of the item
        item_name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")
        print(f"- {item_name}")
    print("-------------------------------------\n")

    # Prompt the user to input a prime part name
    user_input = input("\nEnter the prime part: ").strip()

    # Search for the item in the list of prime parts
    found_item = None
    for item in prime_parts:
        if item.get("i18n", {}).get("en", {}).get("name", "").lower() == user_input.lower():
            found_item = item
            break

    # If the item is not found, inform the user and exit
    if not found_item:
        print(f"Item '{user_input}' not found among prime parts.")
        return

    # If the item is found, fetch its slug and ducat value
    item_slug = found_item.get("slug")
    ducat_value = found_item.get("ducats", 0)
    average_price = wfm_api.get_price(item_slug)

    # Display the results to the user
    print("\n--- Duckums Result ---")
    print(f"Item: {user_input}")
    print(f"Ducat Value: {ducat_value}")
    print(f"Average Market Price: {average_price}")
    print("----------------------\n")

if __name__ == "__main__":
    run_duckums()
