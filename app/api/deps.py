from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import SQLModel, Session
from app.models import CreateSeller
from app.utils.security import decode_access_token
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from app.db import engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/login/access-token")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def _get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload.get("sub"))
    except InvalidTokenError:
        raise credentials_exception

    try:
        user = session.get(CreateSeller, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    except SQLAlchemyError as sqle:
        print(f"Database Error: {sqle}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SQL failed"
        )


CurrentUser = Annotated[CreateSeller, Depends(_get_current_user)]
