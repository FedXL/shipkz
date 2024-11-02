#!/bin/bash


echo "Pulling the latest Docker images..."
if docker-compose pull; then
    echo "Docker images pulled successfully."
else
    echo "Failed to pull Docker images." >&2
    exit 1
fi


echo "Rebuilding and restarting services (excluding the database)..."
if docker-compose up -d --build --no-deps gunicorn daphne celery celery-beat nginx redis; then
    echo "Services restarted successfully."
else
    echo "Failed to restart services." >&2
    exit 1
fi

echo "Checking the status of all containers:"
docker-compose ps





