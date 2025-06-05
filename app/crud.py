from typing import Any, List
from fastapi import HTTPException, Query, status
from sqlmodel import Session, col, select
from sqlalchemy.exc import SQLAlchemyError
from app.models import (
    CreateSeller,
    InputProduct,
    InputSellers,
    InvoiceCreate,
    InvoiceInput,
    InvoicePublic,
    Product,
)
from app.utils.security import verify_password, get_password_hash
from uuid import UUID

"""
CRUD operations for the Sellsers
"""


def create_Seller(*, session: Session, seller: InputSellers) -> CreateSeller:
    """
    Create a new seller in the database.
    """
    seller = CreateSeller.model_validate(seller)  # type: ignore
    seller.password = get_password_hash(seller.password)
    session.add(seller)
    session.commit()
    session.refresh(seller)
    return seller


def get_user_by_email(*, session: Session, email: str) -> CreateSeller | None:
    """
    Get a seller by their email.
    """
    statement = select(CreateSeller).where(CreateSeller.email == email)
    result = session.exec(statement).first()
    if result:
        return result
    else:
        return None


def get_user_by_phoneNumber(
    *, session: Session, phoneNumber: str
) -> CreateSeller | None:
    """
    Get a seller by their phone number.
    """
    try:
        statement = select(CreateSeller).where(CreateSeller.phone_number == phoneNumber)
        result = session.exec(statement).first()
        if result:
            return result
        else:
            return None
    except SQLAlchemyError as sqle:
        print(f"Database Error: {sqle}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SQL failed"
        )


def authenticate(
    *,
    session: Session,
    phoneNumber: str | None = None,
    email: str | None = None,
    password: str,
) -> CreateSeller | None:
    if phoneNumber:
        db_user = get_user_by_phoneNumber(session=session, phoneNumber=phoneNumber)
    elif email:
        db_user = get_user_by_email(session=session, email=email)
    else:
        return None
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


def update_user(
    *, session: Session, user_id: str, user_data: InputSellers
) -> CreateSeller | None:
    """
    Update an existing seller in the database.
    """
    user = session.get(CreateSeller, user_id)
    if not user:
        return None
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


"""
CRUD operations for the Products
"""


def create_product(session: Session, products: List[InputProduct], user_id: UUID):
    """
    Create a new product for the current user
    """
    try:
        for product in products:
            product = Product.model_validate(product, update={"seller_id": user_id})
            session.add(product)
        session.commit()
    except Exception as e:
        print(e)


def get_seller_product(session: Session, seller_id: UUID) -> List[Product]:
    statement = select(Product).where(Product.seller_id == seller_id)
    result = session.exec(statement).all()
    if result:
        return result
    else:
        return []


"""
CRUD operations for the Invoice
"""


def create_invoice(
    session: Session, invoice: InvoiceInput, user_id: UUID
) -> InvoicePublic:
    """
    Create a new invoice in the database.
    """
    invoice = InvoiceCreate.model_validate(invoice, update={"seller_id": user_id})
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


def get_invoice_by_id(session: Session, invoice_id: str) -> InvoicePublic | None:
    """
    Get an invoice by its ID.
    """
    invoice = session.get(InvoiceCreate, UUID(invoice_id))
    if invoice is None:
        return None
    return InvoicePublic.model_validate(invoice)


def get_seller_invoices(
    session: Session,
    user_id: UUID,
    offset: int,
    limit: int,
) -> Any:
    """
    Get all invoices for a specific seller.
    """
    statement = select(InvoiceCreate).order_by(col(InvoiceCreate.created_date).desc())
    statement = statement.where(InvoiceCreate.seller_id == user_id)
    statement = statement.offset(offset).limit(limit)
    invoices = session.exec(statement).all()
    return invoices


def update_invoice(
    session: Session, up_invoice: InvoicePublic, user_id: UUID
) -> InvoiceCreate | None:
    """
    Update an existing invoice in the database.
    """
    db_invoice = session.get(InvoiceCreate, up_invoice.id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if db_invoice.seller_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this invoice.",
        )
    else:
        update_data = up_invoice.model_dump(exclude_unset=True)
        db_invoice = db_invoice.sqlmodel_update(update_data)
        session.add(db_invoice)
        session.commit()
        session.refresh(db_invoice)
    return db_invoice  # type ignore[return-value]


def delete_invoice(session: Session, invoice_id: str) -> None:
    """
    Delete an invoice from the database.
    """
    invoice = session.get(InvoiceCreate, invoice_id)
    if not invoice:
        return None
    session.delete(invoice)
    session.commit()
