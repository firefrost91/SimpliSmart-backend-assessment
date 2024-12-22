from fastapi import APIRouter, Depends, HTTPException
from app.models.organization import Organization as OrganizationModel
router = APIRouter()
from sqlalchemy.orm import Session

def generate_invite_code(length=8):
    """
    Generates a random invite code containing uppercase letters and digits.
    :param length: The length of the invite code (default is 8 characters)
    :return: A string of random characters as the invite code
    """
    # Define the characters that can appear in the invite code (uppercase letters + digits)
    characters = string.ascii_uppercase + string.digits
    invite_code = "".join(random.choices(characters, k=length))
    return invite_code


def generate_unique_invite_code(db: Session, length=8):
    """
    Generates a unique invite code that doesn't already exist in the database.
    :param db: The database session
    :param length: The length of the invite code (default is 8 characters)
    :return: A unique invite code
    """
    invite_code = generate_invite_code(length)

    # Check if the invite code already exists in the database
    while (
        db.query(OrganizationModel)
        .filter(OrganizationModel.invite_code == invite_code)
        .first()
    ):
        # If it exists, generate a new one
        invite_code = generate_invite_code(length)

    return invite_code
