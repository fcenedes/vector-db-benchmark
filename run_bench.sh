#!/bin/bash

export REDIS_PORT=6379
export REDIS_HOST="localhost"
export REDIS_USER=
export REDIS_AUTH=



# Define experiments array
experiments=(
    "redis-m-16-ef-64"
    "redis-m-16-ef-128"
    "redis-m-16-ef-256"
    "redis-m-16-ef-512"
    "redis-m-32-ef-64"
    "redis-m-32-ef-128"
    "redis-m-32-ef-256"
    "redis-m-32-ef-512"
    "redis-m-64-ef-64"
    "redis-m-64-ef-128"
    "redis-m-64-ef-256"
    "redis-m-64-ef-512"
)
# gist-960-euclidean
# Run command for each experiment
for experiment in "${experiments[@]}"; do
    echo "Running experiment: $experiment"
    python run.py --engines "$experiment" --datasets gist-960-euclidean --host "${REDIS_HOST}"
    echo "Completed experiment: $experiment"
    echo "-----------------------------------"
done

echo "All experiments completed!"