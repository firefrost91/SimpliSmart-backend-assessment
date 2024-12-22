from typing import Optional

from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None  # Add the description field here


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    invite_code: str

    class Config:
        from_attributes = True
