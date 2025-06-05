from datetime import datetime
from typing import Annotated
from fastapi import Query
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
import uuid


class BaseSeller(SQLModel):
    name: str | None = None
    email: str | None = None
    phone_number: str = Field(
        max_length=15,
        min_length=10,
        regex=r"^\+?[1-9]\d{1,14}$",
        description="Phone number must be in international format.",
        unique=True,
    )
    store_name: str | None = None
    store_description: str | None = None
    store_address: str | None = None
    insta_link: str | None = None


class InputSellers(BaseSeller):

    password: Annotated[
        str, Query(min_length=8, max_length=30, pattern="[A-Za-z0-9@#$%^&+=]")
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "email": "foo@example.com",
                    "phone_number": "9123456789",
                    "password": "password123",
                    "store_name": "Foo Store",
                    "store_description": "A store that sells foo items.",
                    "store_address": "123 Foo Street, Bar City",
                    "insta_link": "https://instagram.com/foostore",
                }
            ]
        }
    }


class CreateSeller(InputSellers, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    products: list["Product"] = Relationship(back_populates="seller")


class PublicSeller(BaseSeller):
    id: uuid.UUID
    products: list["Product"] = []  # type: ignore[valid-type]


class InvoiceBase(SQLModel):
    customer_name: str | None = None
    customer_phone_number: str | None = None
    customer_email: str | None = None
    customer_address: str | None = None
    status: str | None = Field(default="Pending")
    payment_mode: str | None = Field(default="Cash")
    total_price: float


class InvoiceInput(InvoiceBase):

    invoiceitems: list["InvoiceItems"] = []  # type: ignore[valid-type]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_name": "John Doe",
                    "customer_phone_number": "+1234567890",
                    "customer_email": "johndoe@example.com",
                    "customer_address": "456 Elm Street, Springfield",
                    "created_date": "2023-01-01T12:00:00",
                    "status": "Pending",
                    "payment_mode": "Cash",
                    "total_price": 150.75,
                    "invoiceitems": [
                        {
                            "product_id": "123e4567-e89b-12d3-a456-426614174000",
                            "quantity": 2,
                            "total_price": 50.00,
                        },
                        {
                            "product_id": "123e4567-e89b-12d3-a456-426614174001",
                            "quantity": 1,
                            "total_price": 50.00,
                        },
                    ],
                }
            ]
        }
    }


class InvoiceCreate(InvoiceBase, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default_factory=uuid.uuid4)
    seller_id: uuid.UUID = Field(foreign_key="createseller.id", index=True)
    created_date: datetime = Field(default_factory=datetime.now)

    invoiceitems: list["InvoiceItems"] = Relationship(back_populates="invoice")  # type: ignore[valid-type]


class InvoiceItems(SQLModel, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default_factory=uuid.uuid4)
    invoice_id: uuid.UUID = Field(
        foreign_key="invoicecreate.id", index=True, nullable=False, ondelete="CASCADE"
    )
    product_id: str | None = Field(foreign_key="product.id", nullable=True)
    quantity: int
    total_price: float
    invoice: InvoiceCreate = Relationship(back_populates="invoiceitems")


class InvoicePublic(InvoiceBase):
    id: uuid.UUID
    created_date: datetime
    invoiceitems: list[InvoiceItems] = []


class InputProduct(SQLModel):
    name: str = Field(index=True)
    description: str | None = None
    price: float

    def __eq__(self, other):
        if not isinstance(other, InputProduct):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash((self.name))

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Sample Product",
                    "description": "This is a sample product description.",
                    "price": 29.99,
                }
            ]
        }
    }


class Product(InputProduct, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default_factory=uuid.uuid4)
    seller_id: uuid.UUID = Field(foreign_key="createseller.id", index=True)

    seller: CreateSeller = Relationship(back_populates="products")


class PublicProduct(InputProduct):
    id: uuid.UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
