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
    
    # Loop through the first 20 items in the list
    print("\n------------------------------------------------------")
    for item in prime_parts[:20]:
        # Safely get the name of the item
        item_name = item.get("i18n", {}).get("en", {}).get("name", "Unknown Item")
        print(f"- {item_name}")
    print("------------------------------------------------------\n")
    
    user_input = input("\nEnter the prime part: ").strip()

    found_item = None
    for item in prime_parts:
        if item.get("i18n", {}).get("en", {}).get("name", "").lower() == user_input.lower():
            found_item = item
            break
    
    if not found_item:
        print(f"Item '{user_input}' not found among prime parts.")
        return
    
    item_slug = found_item.get("slug")
    ducat_value = found_item.get("ducats", 0)
    average_price = wfm_api.get_price(item_slug)

    print("\n--- Duckums Result ---")
    print(f"Item: {user_input}")
    print(f"Ducat Value: {ducat_value}")
    print(f"Average Market Price: {average_price}")
    print("----------------------\n")

if __name__ == "__main__":
    run_duckums()
