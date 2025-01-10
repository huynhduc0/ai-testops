#!/bin/bash

# Build the Docker images
docker-compose build

# Bring up the services
docker-compose up -d
