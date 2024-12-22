from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
import jwt  # PyJWT
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import User

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate the current user from the JWT token in the Authorization header.

    This function checks for the presence of a valid JWT token, decodes it to get the user info,
    and raises an HTTPException if the token is invalid or the user is not found in the database.
    """
    # Extract the token from the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = auth_header.split(" ")[1]  # Expecting format: "Bearer <token>"

    try:
        # Decode the token to get user data (sub = username or user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Fetch the user from the database using the decoded username
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

