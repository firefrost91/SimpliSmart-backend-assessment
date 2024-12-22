from app.models.deployment import Deployment, DeploymentStatus


class Scheduler:
    def __init__(self, db):
        self.db = db

    def schedule_deployment(self, deployment, cluster):
        """
        Schedule a deployment by validating and allocating resources.
        """
        # Check if resources are available
        if (
            deployment.cpu_required <= cluster.cpu_available
            and deployment.ram_required <= cluster.ram_available
            and deployment.gpu_required <= cluster.gpu_available
        ):
            # Deduct resources
            cluster.cpu_available -= deployment.cpu_required
            cluster.ram_available -= deployment.ram_required
            cluster.gpu_available -= deployment.gpu_required
            self.db.commit()
            return True
        else:
            # Attempt to preempt lower-priority deployments
            return self.preempt_deployments(deployment, cluster)

    def preempt_deployments(self, deployment, cluster):
        """
        Preempt lower-priority deployments to free resources.
        """
        # Query the lower-priority deployments that are still pending
        print("PREEMPTING")
        lower_priority_deployments = (
            self.db.query(Deployment)
            .filter(
                Deployment.cluster_id == cluster.id,
                Deployment.status == DeploymentStatus.COMPLETED,
                Deployment.priority
                > deployment.priority,  # Only preempt lower-priority deployments
            )
            .order_by(Deployment.priority)  # Ascending order of priority
            .all()
        )

        for lower_deployment in lower_priority_deployments:
            print(
                f"PREEMPTING Deployment {lower_deployment.id}: "
                f"CPU={lower_deployment.cpu_required}, RAM={lower_deployment.ram_required}, GPU={lower_deployment.gpu_required}"
            )

            # Free resources allocated to the lower-priority deployment
            cluster.cpu_available += lower_deployment.cpu_required
            cluster.ram_available += lower_deployment.ram_required
            cluster.gpu_available += lower_deployment.gpu_required

            # Mark the lower-priority deployment as FAILED
            lower_deployment.status = DeploymentStatus.FAILED
            print(f"Deployment {lower_deployment.id} status updated to FAILED.")

            # Persist changes to the database
            self.db.commit()

            # Re-check if enough resources are now available for the new deployment
            if (
                deployment.cpu_required <= cluster.cpu_available
                and deployment.ram_required <= cluster.ram_available
                and deployment.gpu_required <= cluster.gpu_available
            ):
                print("Enough resources freed. Scheduling the deployment...")
                cluster.cpu_available -= deployment.cpu_required
                cluster.ram_available -= deployment.ram_required
                cluster.gpu_available -= deployment.gpu_required
                self.db.commit()
                return True

        # If we exit the loop and still don’t have enough resources, return False
        print("Could not free enough resources for the deployment.")
        return False
