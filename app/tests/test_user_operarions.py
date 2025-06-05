from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routers import login, signup, users

# Create a FastAPI app instance and include routers
app = FastAPI()
app.include_router(login.router)
app.include_router(signup.router)
app.include_router(users.router)


client = TestClient(app)

from app.models import InputProduct, InvoiceInput


def get_auth_headers(email, password, phone_number):
    # Helper to sign up and get auth headers
    signup_data = {
        "name": "UserOps_Test",
        "email": email,
        "phone_number": phone_number,
        "password": password,
    }
    client.post("/signup", json=signup_data)
    token_resp = client.post(
        "/login/access-token",
        params={"email": email, "password": password},
    )
    token = token_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_product():
    headers = get_auth_headers("produser@example.com", "prodpass1245", "09223456789")
    products = [
        {"name": "ProductA", "price": 10.0},
        {"name": "ProductB", "price": 20.0},
        {"name": "ProductC", "price": 30.0},
        {"name": "ProductC", "price": 30.0},
    ]
    response = client.post("/user/newproduct", json=products, headers=headers)
    assert response.status_code == 200
    names = [product["name"] for product in response.json()]
    assert names.count("ProductA") == 1
    assert names.count("ProductB") == 1
    assert names.count("ProductC") == 1


def test_create_duplicate_product():
    headers = get_auth_headers("dupuser@example.com", "duppass1234", "09345678901")
    products = [
        {"name": "ProductX", "price": 10.0},
        {"name": "ProductX", "price": 10.0},
    ]
    # First creation should succeed
    first_response = client.post("/user/newproduct", json=products, headers=headers)
    assert first_response.status_code == 200

    # Second creation with the same product should fail
    duplicate_response = client.post("/user/newproduct", json=products, headers=headers)
    assert duplicate_response.status_code == 400
    assert "already exist" in duplicate_response.json().get("detail", "")


"""
for invoice first i need to get products id then create one.
i need to create get product api
"""


def test_create_invoice():
    headers = get_auth_headers("invuser@example.com", "invpass3773", "09988765432")
    # creating some products
    products = [
        {"name": "ProductA", "price": 10.0},
        {"name": "ProductB", "price": 20.0},
        {"name": "ProductC", "price": 30.0},
    ]
    response = client.post("/user/newproduct", json=products, headers=headers)

    products_id = [product["id"] for product in response.json()]
    invoice = {
        "customer_name": "Customer1",
        "customer_phone_number": "+1234567890",
        "customer_email": "johndoe@example.com",
        "customer_address": "456 Elm Street, Springfield",
        "created_date": "2023-01-01T12:00:00",
        "status": "Pending",
        "payment_mode": "Cash",
        "total_price": 150.75,
        "invoiceitems": [
            {
                "product_id": products_id[1],
                "quantity": 2,
                "total_price": 50.00,
            },
            {
                "product_id": products_id[2],
                "quantity": 1,
                "total_price": 50.00,
            },
        ],
    }
    response = client.post("/user/createInvoice", json=invoice, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Customer1"
    assert "id" in data and data["id"] is not None


def test_update_invoice():
    headers = get_auth_headers(
        "invuserupdate@example.com", "invpass3773", "09988777432"
    )
    # creating some products
    products = [
        {"name": "ProductA", "price": 10.0},
        {"name": "ProductB", "price": 20.0},
        {"name": "ProductC", "price": 30.0},
    ]
    response = client.post("/user/newproduct", json=products, headers=headers)
    products_id = [product["id"] for product in response.json()]
    # create an invoice first
    invoice = {
        "customer_name": "Customer1",
        "customer_phone_number": "+1234567890",
        "customer_email": "johndoe@example.com",
        "status": "Pending",
        "payment_mode": "Cash",
        "total_price": 70.0,
        "invoiceitems": [
            {
                "product_id": products_id[1],
                "quantity": 2,
                "total_price": 40.00,
            },
            {
                "product_id": products_id[2],
                "quantity": 1,
                "total_price": 30.00,
            },
        ],
    }
    response = client.post("/user/createInvoice", json=invoice, headers=headers)
    inv_id = response.json()["id"]
    date = response.json()["created_date"]
    # update the invoice
    up_invoice = {
        "id": inv_id,
        "customer_name": "upCustomer",
        "customer_phone_number": "+1234567890",
        "customer_email": "johndoe@example.com",
        "created_date": date,
        "status": "Paid",
        "total_price": 70.0,
        "invoiceitems": [
            {
                "product_id": products_id[1],
                "quantity": 2,
                "total_price": 40.00,
            },
            {
                "product_id": products_id[2],
                "quantity": 1,
                "total_price": 30.00,
            },
        ],
    }

    response = client.patch("/user/update_invoice", json=up_invoice, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "upCustomer"


def test_update_user_password_success():
    email = "pwchange@example.com"
    password = "oldpw292902"
    headers = get_auth_headers(email, password, "09123666789")
    response = client.post(
        "/user/new_password",
        headers=headers,
        params={"current_password": "oldpw292902", "new_password": "newpw548548"},
    )
    assert response.status_code == 200
    assert "Password updated" in response.json()["message"]


def test_update_user_password_wrong_current():
    email = "pwfail@example.com"
    password = "rightpw49349"
    headers = get_auth_headers(email, password, "09123456999")
    response = client.post(
        "/user/new_password",
        headers=headers,
        params={"current_password": "wrongpw", "new_password": "newpw34985"},
    )
    assert response.status_code == 400
    assert "Incorrect password" in response.json()["detail"]


def test_update_user_info():
    email = "infouser@example.com"
    password = "infopw21838df"
    headers = get_auth_headers(email, password, "09123456888")
    update_data = {
        "name": "Updated Name",
        "email": "infouser_updated@example.com",
        "phone_number": "09123456777",
        "address": "123 Updated St, City",
    }
    response = client.patch("/user/update_info", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_get_user_invoice():
    email = "getinvuser@example.com"
    password = "getinvpass123"
    phone_number = "09123456701"
    headers = get_auth_headers(email, password, phone_number)

    # Create some products
    products = [
        {"name": "Product1", "price": 15.0},
        {"name": "Product2", "price": 25.0},
    ]
    prod_resp = client.post("/user/newproduct", json=products, headers=headers)
    assert prod_resp.status_code == 200
    products_id = [product["id"] for product in prod_resp.json()]

    # Create two invoices
    invoice1 = {
        "customer_name": "CustomerA",
        "customer_phone_number": "+1111111111",
        "customer_email": "a@example.com",
        "customer_address": "Addr1",
        "created_date": "2023-01-01T10:00:00",
        "status": "Pending",
        "payment_mode": "Cash",
        "total_price": 40.0,
        "invoiceitems": [
            {
                "product_id": products_id[0],
                "quantity": 2,
                "total_price": 30.0,
            }
        ],
    }
    invoice2 = {
        "customer_name": "CustomerB",
        "customer_phone_number": "+2222222222",
        "customer_email": "b@example.com",
        "customer_address": "Addr2",
        "created_date": "2023-01-02T11:00:00",
        "status": "Paid",
        "payment_mode": "Card",
        "total_price": 25.0,
        "invoiceitems": [
            {
                "product_id": products_id[1],
                "quantity": 1,
                "total_price": 25.0,
            }
        ],
    }
    resp1 = client.post("/user/createInvoice", json=invoice1, headers=headers)
    resp2 = client.post("/user/createInvoice", json=invoice2, headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # Now get invoices
    get_resp = client.get("/user/get_invoices", headers=headers)
    assert get_resp.status_code == 200
    invoices = get_resp.json()
    assert isinstance(invoices, list)
    # Should contain at least the two created invoices
    customer_names = [inv["customer_name"] for inv in invoices]
    assert "CustomerA" in customer_names
    assert "CustomerB" in customer_names
