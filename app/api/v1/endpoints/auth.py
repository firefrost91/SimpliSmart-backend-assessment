from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core import deps, security
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/login")
async def login(
        request: Request,
        response: Response,
        username: str,
        password: str,
        db: Session = Depends(deps.get_db)
):
    """
    Login endpoint: Verifies user credentials and sets user_id in session.
    """
    # Find the user by username
    user = db.query(UserModel).filter(UserModel.username == username).first()
    print(user, "USER")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify the password
    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Set user_id in session
    request.session["user_id"] = user.id

    # Return success message
    return JSONResponse(
        content={"message": "Successfully logged in"},
        status_code=status.HTTP_200_OK
    )


@router.post("/register", response_model=User)
async def register(
        *,
        db: Session = Depends(deps.get_db),
        user_in: UserCreate
):
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Hash the password before storing it
    hashed_password = security.get_password_hash(user_in.password)

    # Create the user
    new_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        organization_id = user_in.organization_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/logout")
async def logout(request: Request):
    """
    Logout endpoint: Clears the session to log out the user.
    """
    request.session.clear()

    return JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=status.HTTP_200_OK
    )
