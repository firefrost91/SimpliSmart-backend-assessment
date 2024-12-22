from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.organization import Organization, OrganizationCreate
from app.models.user import User
from app.models.organization import Organization as OrganizationModel

router = APIRouter()
from sqlalchemy.orm import Session

import random
import string

def generate_invite_code(length=8):
    """
    Generates a random invite code containing uppercase letters and digits.
    :param length: The length of the invite code (default is 8 characters)
    :return: A string of random characters as the invite code
    """
    # Define the characters that can appear in the invite code (uppercase letters + digits)
    characters = string.ascii_uppercase + string.digits
    invite_code = ''.join(random.choices(characters, k=length))
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
    while db.query(OrganizationModel).filter(OrganizationModel.invite_code == invite_code).first():
        # If it exists, generate a new one
        invite_code = generate_invite_code(length)

    return invite_code


@router.post("/", response_model=Organization)
def create_organization(
        *,
        db: Session = Depends(deps.get_db),
        organization_in: OrganizationCreate,
        current_user: User = Depends(deps.get_current_user)
):
    """
    Implement organization creation.
    This will create a new organization and associate it with the current user.
    """
    # Check if the user is already part of an organization
    print(current_user, "CURRENT")
    print(organization_in, "ORG")
    invite_code = generate_unique_invite_code(db)
    if current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="User is already part of an organization"
        )

    # Check if organization already exists
    existing_org = db.query(OrganizationModel).filter(OrganizationModel.name == organization_in.name).first()
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Organization already exists"
        )

    # Create the new organization
    new_org = OrganizationModel(
        name=organization_in.name,
        invite_code = invite_code
        # description=organization_in.description,
        # owner_id=current_user.id  # Set the current user as the owner
    )

    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # Assign the organization to the current user
    current_user.organization_id = new_org.id
    db.commit()

    return new_org


@router.post("/{invite_code}/join")
def join_organization(
        *,
        db: Session = Depends(deps.get_db),
        invite_code: str,
        current_user: User = Depends(deps.get_current_user)
):
    """
    Implement organization joining logic.
    This will allow a user to join an organization using an invite code.
    """
    # Find the organization using the invite code
    organization = db.query(OrganizationModel).filter(OrganizationModel.invite_code == invite_code).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    # Check if the user is already part of an organization
    if current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="User is already part of an organization"
        )

    # Assign the user to the organization
    current_user.organization_id = organization.id
    db.commit()

    return {"message": f"Successfully joined the organization {organization.name}"}
