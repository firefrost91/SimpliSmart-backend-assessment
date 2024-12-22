import json
import logging
from sqlmodel import Session
from app.queue.consumer import RabbitMQConsumer
from app.db.session import engine
from app.scheduler.scheduler import Scheduler
from app.models.deployment import DeploymentStatus

# Configure logging
logging.basicConfig()
logger = logging.getLogger(__name__)

def process_deployment(ch, method, properties, body):
    """Process deployment messages"""
    try:
        print("NEW DEPLOYMENT")
        data = json.loads(body)
        with Session(engine) as db:
            scheduler = Scheduler(db)
            success = scheduler.process_deployment(data['deployment_id'])

            if success:
                logger.info(f"Deployment {data['deployment_id']} processed successfully.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Requeue if failed (with retry limit)
                if data.get('retry_count', 0) < 3:
                    data['retry_count'] = data.get('retry_count', 0) + 1
                    ch.basic_publish(
                        exchange='',
                        routing_key=method.routing_key,
                        body=json.dumps(data)
                    )
                    logger.warning(f"Requeueing deployment {data['deployment_id']} for retry.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing deployment: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def main():
    consumer = RabbitMQConsumer()

    # Start consuming from priority queues
    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info(" [*] Stopping worker...")

if __name__ == "__main__":
    main()
