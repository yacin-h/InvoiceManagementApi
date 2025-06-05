from fastapi.testclient import TestClient
from app.api.routers import signup

example_sellers = [
    {
        "name": "Alice's Supplies",
        "email": "alice@example.com",
        "phone_number": "09381234567",
        "password": "securepassword123",
        "store_name": "Alice's Supplies",
        "store_description": "",
        "store_address": "123 Main St, Springfield",
        "insta_link": "",
    },
    {
        "name": "Delta Hardware",
        "email": "delta@hardware.com",
        "phone_number": "09110001122",
        "password": "deltapass2024",
        "store_name": "Delta Hardware",
        "store_description": "Tools and building materials.",
        "store_address": "101 Industrial Rd, Springfield",
        "insta_link": "https://instagram.com/deltahardware",
    },
    {
        "name": "Echo Fashion",
        "email": "echo@fashion.com",
        "phone_number": "09220002233",
        "password": "echofashion!",
        "store_name": "Echo Fashion",
        "store_description": "Trendy clothes and accessories.",
        "store_address": "202 Fashion Ave, Shelbyville",
        "insta_link": "https://instagram.com/echofashion",
    },
    {
        "name": "Foxtrot Groceries",
        "email": "foxtrot@groceries.com",
        "phone_number": "09330003344",
        "password": "foxtrotgroceries2024",
        "store_name": "Foxtrot Groceries",
        "store_description": "Fresh groceries and daily needs.",
        "store_address": "303 Market St, Capital City",
        "insta_link": "https://instagram.com/foxtrotgroceries",
    },
]


def create_dummy_sellers_test():
    """
    Create dummy sellers for testing purposes.
    """
    with TestClient(signup.router) as client:
        for seller in example_sellers:
            response = client.post("/signup", json=seller)
            if response.status_code != 200:
                print(f"Failed to create seller: {response.json()}")
            else:
                print(f"Created seller: {response.json()}")


create_dummy_sellers_test()
