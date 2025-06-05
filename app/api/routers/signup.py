from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.models import InputSellers, PublicSeller, InvoicePublic
from app.api.deps import SessionDep
from app import crud

router = APIRouter()


@router.post("/signup", tags=["signup"], response_model=PublicSeller)
def signup_user(inputseller: InputSellers, session: SessionDep) -> Any:

    seller = crud.get_user_by_phoneNumber(
        session=session, phoneNumber=inputseller.phone_number
    )
    if seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this Phone Number already exists in the system.",
        )
    seller = crud.get_user_by_email(session=session, email=inputseller.email)
    if seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    return crud.create_Seller(session=session, seller=inputseller)


@router.get("/invoice", tags=["Direct Lint to Invoice"], response_model=InvoicePublic)
def get_invoice(id: str, session: SessionDep) -> Any:

    return crud.get_invoice_by_id(session=session, invoice_id=id)
