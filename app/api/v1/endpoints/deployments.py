from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.deployment import DeploymentStatus
from app.models.user import User
from app.models.cluster import Cluster as DBCluster
from app.models.deployment import Deployment as DBDeployment
from app.queue.producer import publish_deployment_task  # Import the producer function


router = APIRouter()

@router.post("/", response_model=Deployment)
def create_deployment(
    *,
    db: Session = Depends(deps.get_db),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new deployment and schedule it.
    """
    # Check if the specified cluster exists
    cluster = db.query(DBCluster).filter(DBCluster.id == deployment_in.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Check if the user has access to the cluster
    if current_user.organization_id != cluster.organization_id:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to create a deployment in this cluster"
        )

    # Validate cluster resource availability
    if deployment_in.cpu_required > cluster.cpu_available:
        raise HTTPException(status_code=400, detail="Insufficient CPU resources in the cluster")
    if deployment_in.ram_required > cluster.ram_available:
        raise HTTPException(status_code=400, detail="Insufficient RAM resources in the cluster")
    if deployment_in.gpu_required > cluster.gpu_available:
        raise HTTPException(status_code=400, detail="Insufficient GPU resources in the cluster")

    # Deduct resources from the cluster
    cluster.cpu_available -= deployment_in.cpu_required
    cluster.ram_available -= deployment_in.ram_required
    cluster.gpu_available -= deployment_in.gpu_required

    # Create the deployment record
    deployment = DBDeployment(
        name=deployment_in.name,
        docker_image=deployment_in.docker_image,
        cpu_required=deployment_in.cpu_required,
        ram_required=deployment_in.ram_required,
        gpu_required=deployment_in.gpu_required,
        priority=deployment_in.priority,
        cluster_id=deployment_in.cluster_id,
        status=DeploymentStatus.PENDING  # Initial status is PENDING
    )

    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    # Publish deployment task to the queue (if applicable)
    publish_deployment_task(deployment_id=deployment.id, priority=deployment.priority)

    return deployment

@router.get("/", response_model=List[Deployment])
def list_deployments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all deployments that the user has access to.
    """
    # Fetch all clusters associated with the user's organization
    clusters = db.query(DBCluster).filter(DBCluster.organization_id == current_user.organization_id).all()

    if not clusters:
        raise HTTPException(status_code=404, detail="No clusters found for your organization")

    # Fetch all deployments in these clusters
    deployments = db.query(DBDeployment).filter(DBDeployment.cluster_id.in_([cluster.id for cluster in clusters])).all()

    if not deployments:
        raise HTTPException(status_code=404, detail="No deployments found for your clusters")

    return deployments