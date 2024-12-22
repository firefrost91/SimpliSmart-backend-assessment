import json

import pika


def publish_deployment_task(deployment_id: int, priority: int):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )  # Adjust RabbitMQ server URL
    channel = connection.channel()

    # Declare the queue (make sure it exists)
    channel.queue_declare(queue="deployment_queue", durable=True)

    # Message format
    message = {"deployment_id": deployment_id, "priority": priority}

    # Publish the message
    channel.basic_publish(
        exchange="",
        routing_key="deployment_queue",
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make the message persistent
        ),
    )
    print(f" [x] Sent deployment task for deployment_id: {deployment_id}")
    connection.close()
