from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import deps
from app.models.cluster import Cluster as DBCluster
from app.models.user import User
from app.schemas.cluster import Cluster, ClusterCreate

router = APIRouter()


@router.post("/", response_model=Cluster)
def create_cluster(
    *,
    db: Session = Depends(deps.get_db),
    cluster_in: ClusterCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new cluster.
    """
    # Example: Check if the user has permission to create a cluster
    if current_user.organization_id is not cluster_in.organization_id:
        raise HTTPException(
            status_code=400,
            detail="User not allowed to create a cluster in this organization",
        )
    # Create the cluster in the database
    cluster = DBCluster(
        name=cluster_in.name,
        cpu_limit=cluster_in.cpu_limit,
        ram_limit=cluster_in.ram_limit,
        gpu_limit=cluster_in.gpu_limit,
        organization_id=cluster_in.organization_id,
        cpu_available=cluster_in.cpu_limit,  # Assuming available resources are the same as limits
        ram_available=cluster_in.ram_limit,
        gpu_available=cluster_in.gpu_limit,
    )

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return cluster


@router.get("/", response_model=List[Cluster])
def list_clusters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    clusters = (
        db.query(DBCluster)
        .filter(DBCluster.organization_id == current_user.organization_id)
        .all()
    )
    if not clusters:
        raise HTTPException(
            status_code=404, detail="No clusters found for this organization"
        )

    return clusters
