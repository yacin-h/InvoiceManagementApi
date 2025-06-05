from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.models import Token, PublicSeller
from app.utils.security import create_access_token
from app import crud
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    *,
    session: SessionDep,
    phoneNumber: str | None = None,
    email: str | None = None,
    password: str,
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    seller = crud.authenticate(
        session=session, phoneNumber=phoneNumber, email=email, password=password
    )
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number, email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=seller.id)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/login/me", response_model=PublicSeller)
def read_user(current_user: CurrentUser) -> Any:
    """
    Get current user information
    """
    return current_user
