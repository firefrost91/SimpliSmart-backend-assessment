import pika
import json
from app.db.session import SessionLocal
from app.models.cluster import Cluster
from app.models.deployment import DeploymentStatus, Deployment
from app.scheduler.scheduler import Scheduler


class RabbitMQConsumer:
    def __init__(self, queue_name='deployment_queue', rabbitmq_url='localhost'):
        self.queue_name = queue_name
        self.rabbitmq_url = rabbitmq_url

    def process_deployment(self, ch, method, properties, body):
        """
        Process deployment tasks with scheduling logic.
        """
        try:
            # Parse the message body
            data = json.loads(body)
            deployment_id = data.get('deployment_id')

            if not deployment_id:
                print("Invalid message: Missing deployment_id.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            with SessionLocal() as db:
                # Fetch deployment and its associated cluster in a single transaction
                deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
                if not deployment:
                    print(f"Deployment {deployment_id} not found.")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                cluster = db.query(Cluster).filter(Cluster.id == deployment.cluster_id).first()
                if not cluster:
                    print(f"Cluster not found for Deployment {deployment_id}.")
                    self.mark_deployment_status(db, deployment, DeploymentStatus.FAILED)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Schedule the deployment
                scheduler = Scheduler(db)
                if scheduler.schedule_deployment(deployment, cluster):
                    print(f"Deployment {deployment_id} is now RUNNING.")
                    self.execute_deployment(deployment)
                    self.mark_deployment_status(db, deployment, DeploymentStatus.COMPLETED)
                else:
                    print(f"Deployment {deployment_id} could not be scheduled.")
                    self.mark_deployment_status(db, deployment, DeploymentStatus.FAILED)

                # Acknowledge message after processing
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing deployment: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Reject and do not requeue on failure

    def mark_deployment_status(self, db, deployment, status):
        """
        Update the status of a deployment and commit the change.
        """
        deployment.status = status
        db.commit()

    def execute_deployment(self, deployment):
        """
        Simulate deployment execution.
        Replace this method with actual deployment execution logic.
        """
        print(f"Executing deployment {deployment.id}...")

    def start_consuming(self):
        """
        Start consuming messages from RabbitMQ queue.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_url))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=self.queue_name, durable=True)

        # Set up the consumer
        channel.basic_qos(prefetch_count=1)  # Process one task at a time
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.process_deployment)

        print(f' [*] Waiting for messages in queue: {self.queue_name}...')
        channel.start_consuming()

