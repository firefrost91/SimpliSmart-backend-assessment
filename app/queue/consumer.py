import pika
import json
from sqlmodel import Session
from app.db.session import SessionLocal
from app.db.session import engine
from app.models.cluster import Cluster  # Adjust path to where Cluster is defined
from app.models.deployment import DeploymentStatus
from app.models.deployment import Deployment
from app.scheduler.scheduler import Scheduler

class RabbitMQConsumer:
    def __init__(self, queue_name='deployment_queue', rabbitmq_url='localhost'):
        self.queue_name = queue_name
        self.rabbitmq_url = rabbitmq_url

    def process_deployment(self, ch, method, properties, body):
        """
        Process deployment task
        """
        try:
            data = json.loads(body)
            deployment_id = data['deployment_id']
            priority = data['priority']


            # Open a new session to interact with the database
            with SessionLocal() as db:
                # Example: Use a scheduler to handle deployment
                scheduler = Scheduler(db)
                success = scheduler.process_deployment(deployment_id)
                print("/n" , success, "SUCCESS /n")

                # If the deployment is successfully processed
                if success:
                    # Update the deployment status in the DB
                    print("PREDEPLOY", deployment_id, db)
                    deployments = db.query(Deployment).all()
                    print("ALL DEPS", deployments)

                    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
                    print("DEPLOY", deployment)
                    if deployment:
                        deployment.status = DeploymentStatus.COMPLETED
                        db.commit()
                        print(f"Deployment {deployment_id} processed successfully")
                    else:
                        print(f"Deployment {deployment_id} not found in the database.")
                else:
                    # Handle failure (e.g., retry or update status)
                    print(f"Deployment {deployment_id} failed")

                # Acknowledge the message after processing
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing deployment: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Reject and do not requeue on failure

    def start_consuming(self, queue: str, on_message_callback):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Adjust RabbitMQ server URL
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=queue, durable=True)

        # Set up the consumer
        channel.basic_qos(prefetch_count=1)  # Process one task at a time
        channel.basic_consume(queue=queue, on_message_callback=on_message_callback)

        print(f' [*] Waiting for messages in queue: {queue}...')
        channel.start_consuming()
