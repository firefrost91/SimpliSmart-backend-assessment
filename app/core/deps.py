from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validate the current user from the session.

    This function checks for the user ID in the session, queries the database to ensure the user exists,
    and raises an HTTPException if the user is not authenticated or not found.
    """
    # Retrieve user ID from the session (this assumes your app is using session cookies or other mechanisms)
    print(request.session, "REQUEST")
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    # If user is not found, raise an error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Return the user object
    return user
