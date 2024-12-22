from fastapi import APIRouter, Depends, HTTPException
from app.core import deps
from app.models.organization import Organization as OrganizationModel
from app.models.user import User
from app.schemas.organization import Organization, OrganizationCreate
from app.utils.invite_utils import generate_invite_code, generate_unique_invite_code

router = APIRouter()
from sqlalchemy.orm import Session



@router.post("/", response_model=Organization)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(deps.get_current_user),
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
            status_code=400, detail="User is already part of an organization"
        )

    # Check if organization already exists
    existing_org = (
        db.query(OrganizationModel)
        .filter(OrganizationModel.name == organization_in.name)
        .first()
    )
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization already exists")

    # Create the new organization
    new_org = OrganizationModel(
        name=organization_in.name,
        invite_code=invite_code
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
    current_user: User = Depends(deps.get_current_user),
):
    """
    Implement organization joining logic.
    This will allow a user to join an organization using an invite code.
    """
    # Find the organization using the invite code
    organization = (
        db.query(OrganizationModel)
        .filter(OrganizationModel.invite_code == invite_code)
        .first()
    )

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if the user is already part of an organization
    if current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is already part of an organization"
        )

    # Assign the user to the organization
    current_user.organization_id = organization.id
    db.commit()

    return {"message": f"Successfully joined the organization {organization.name}"}
