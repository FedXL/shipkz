#!/bin/bash

echo "Pulling the latest Docker images..."
docker-compose pull
echo "...SUCCESS!"
docker-compose up -d --build --no-deps gunicorn daphne celery celery-beat nginx redis
docker-compose ps




