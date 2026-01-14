#!/bin/bash

############### Redis ENV VARS #################
export REDIS_PORT=6739
export REDIS_HOST=psc.122222.eu-west1-mz.gcp.cloud.rlrcp.com
export REDIS_USER=default
export REDIS_AUTH=performance
############### General ENV VARS #################
# Define DATASETS env var - default to gist-960-euclidean if not set
export DATASETS=${BENCH_DATASETS:-"gist-960-euclidean"}
export ENGINES=${BENCH_ENGINES:-"redis"}
############### MONGO ENV VARS #################
export MONGO_PORT=${MONGO_PORT:-"27017"}
export MONGO_HOST=${MONGO_HOST:-"cluster0.1234567.mongodb.net"}
export MONGO_AUTH=${MONGO_AUTH:-"performance"}
export MONGO_USER=${MONGO_USER:-"performance"}
export MONGO_READ_PREFERENCE=${MONGO_READ_PREFERENCE:-"primary"}
export MONGO_WRITE_CONCERN=${MONGO_WRITE_CONCERN:-"1"}
export EMBEDDING_FIELD_NAME=${EMBEDDING_FIELD_NAME:-"embedding"}
export ATLAS_DB_NAME=${ATLAS_DB_NAME:-"vector-db"}
export ATLAS_COLLECTION_NAME=${ATLAS_COLLECTION_NAME:-"vector-collection"}
export ATLAS_VECTOR_SEARCH_INDEX_NAME=${ATLAS_VECTOR_SEARCH_INDEX_NAME:-"vector-index"}

#activate poetry shell
# shellcheck disable=SC2046
. $(poetry env info --path)/bin/activate
# Define experiments array for redis vs mongo
# shellcheck disable=SC2034
experiments_redis_mongo=(
    "redis-default-simple" # default is M 16 - EF_CONSTRUCTION 200
    "mongodb-default" # default is M 16 - EF_CONSTRUCTION 200
)
# Define experiments array for redis
experiments_redis=(
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
echo "-----------------------------------"
echo "Running experiment: redis-default-simple - Redis VS MongoDB - Default"
python run.py --engines "redis-default-simple" --datasets "${DATASETS}" --host "${REDIS_HOST}"
echo "Completed experiment: redis-default-simple"
echo "-----------------------------------"
echo "Running experiment: mongodb-default - Redis VS MongoDB - Default"
python run.py --engines "mongodb-default" --datasets "${DATASETS}" --host "${MONGO_HOST}"
echo "Completed experiment: mongodb-default"
echo "-----------------------------------"
echo "Redis VS MongoDB - Default completed!"
# gist-960-euclidean
# Run command for each experiment
for experiment in "${experiments_redis[@]}"; do
    echo "Running experiment: $experiment - Redis"
    python run.py --engines "$experiment" --datasets "${DATASETS}" --host "${REDIS_HOST}"
    echo "Completed experiment: $experiment"
    echo "-----------------------------------"
done

echo "All experiments completed!"