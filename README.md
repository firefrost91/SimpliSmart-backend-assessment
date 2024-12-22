# Simplismart backend assignment

## Overview

This project is a **hypervisor-like service** that enables the efficient management of virtualized resources through a **FastAPI** application, **PostgreSQL** for storage, and **RabbitMQ** for deployment scheduling. It allows users to create, manage, and monitor deployments and clusters.

## Features

- **Hypervisor-like functionality**: Manage deployments, clusters and resources.
- **PostgreSQL for data storage**: Scalable and reliable relational database for storing configurations and metadata.
- **RabbitMQ for messaging**: Efficient communication between services for resource allocation and monitoring.
- **JWT Authentication**: Secure authentication using JWT to access protected APIs.
- **FastAPI for high performance**: Built with FastAPI to ensure low-latency API responses and async processing.

## Architecture

The project consists of the following components:
- **FastAPI**: API server for managing requests (REST or WebSocket).
- **PostgreSQL**: Database for persisting user and VM data.
- **RabbitMQ**: Message broker for managing asynchronous tasks like VM provisioning, monitoring, etc.

## Installation

### Prerequisites

- Python 3.11
- PostgreSQL
- RabbitMQ
- Docker(to run RabbitMQ instance locally, if required)

### 1. Clone the repository
```bash
git clone https://github.com/firefrost91/SimpliSmart-backend-assessment.git
cd SimpliSmart-backend-assessment
```

### 2. Setup local environment
```bash
python -m venv venv
source venv/bin/activate  # For Unix/macOS
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
```

### 3. Configure environment variables
Update the environment variables:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Session Configuration
SECRET_KEY=your-secret-key  # For secure session encryption
SESSION_COOKIE_NAME=session  # Cookie name for the session
SESSION_MAX_AGE=1800
```

### 4. Setup RabbitMQ locally
Pull the RabbitMQ docker image:
```bash
docker pull rabbitmq:management
```
Once the image is downloaded, you can run RabbitMQ in a Docker container using this command:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```
Once RabbitMQ is running, you can access the RabbitMQ management web UI by accessing **http://localhost:15672**

The default login credentials are:

- **Username**: guest
- **Password**: guest

Run the worker to listen to messages and consume them 
```bash
python -m worker.main
```
### 5. Run the FastAPI application locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
### 6. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 7. You are ready to go!
Try hitting the APIs using the Postman collection (apis-v1-collection.json) or any other API client of your choice.
