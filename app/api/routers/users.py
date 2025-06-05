from typing import Any, List
from fastapi import APIRouter, HTTPException, Query
from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.models import (
    InvoiceInput,
    InvoicePublic,
    BaseSeller,
    InputProduct,
    PublicSeller,
    PublicProduct,
)
from app.utils.security import get_password_hash, verify_password


router = APIRouter(prefix="/user", tags=["user operations"])


@router.post("/newproduct", response_model=List[PublicProduct])
def create_product(
    products: List[InputProduct], session: SessionDep, current_user: CurrentUser
):
    """
    Create a new product for the current user
    """
    # trun it into set to avoid duplicates
    products = set(products)  # type: ignore[assignment]
    seller_products = crud.get_seller_product(
        session=session, seller_id=current_user.id
    )
    if len(seller_products) > 0:
        seller_products_names = [p.name for p in seller_products]  # type: ignore

        # trun it into set for faster lookup
        seller_products_names = set(seller_products_names)  # type: ignore[assignment]
        products = [
            product for product in products if product.name not in seller_products_names
        ]
        if products == []:
            raise HTTPException(
                status_code=400, detail=f"All Products already exist for this seller."
            )
    crud.create_product(session=session, products=products, user_id=current_user.id)
    seller_products = crud.get_seller_product(
        session=session, seller_id=current_user.id
    )
    return list(seller_products)


@router.post("/createInvoice", response_model=InvoicePublic)
def create_invoice(
    invoice: InvoiceInput,
    session: SessionDep,
    current_user: CurrentUser,
) -> InvoicePublic:
    """
    Create an invoice for the current user
    """
    new_invoice = crud.create_invoice(
        session=session, invoice=invoice, user_id=current_user.id
    )
    return new_invoice


@router.get("/get_invoices", response_model=List[InvoicePublic])
def get_invoices(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: int = Query(default=10, le=10),
) -> Any:
    """
    Get all invoices for the current user
    """
    invoices = crud.get_seller_invoices(
        session=session, user_id=current_user.id, offset=offset, limit=limit
    )
    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found")
    return list(invoices)


@router.patch("/update_invoice", response_model=InvoicePublic)
def update_invoice(
    up_invoice: InvoicePublic, session: SessionDep, current_user: CurrentUser
):
    """
    Update an existing invoice for the current user
    """
    new_invoice = crud.update_invoice(
        session=session, up_invoice=up_invoice, user_id=current_user.id
    )
    return new_invoice


@router.post("/new_password")
def update_user_password(
    session: SessionDep,
    current_user: CurrentUser,
    current_password: str,
    new_password: str,
):
    """
    Update the password for the current user
    """

    if not verify_password(current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if current_password == new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(new_password)
    current_user.password = hashed_password
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": "Password updated successfully."}


@router.patch("/update_info", response_model=PublicSeller)
def update_user_me(
    *, session: SessionDep, user_in: BaseSeller, current_user: CurrentUser
) -> Any:
    """
    Update user info.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)  # type: ignore
    current_user.sqlmodel_update(user_data)  # type: ignore
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
