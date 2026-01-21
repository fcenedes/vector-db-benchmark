#!/bin/bash

############### Redis ENV VARS #################
export REDIS_PORT=${DB_PORT:-6739}
export REDIS_HOST=${PRIVATE_ENDPOINT:-"psc.122222.eu-west1-mz.gcp.cloud.rlrcp.com"}
export REDIS_USER=${REDIS_RW_USER:-"default"}
export REDIS_AUTH=${REDIS_RW_PASSWORD:-"REPLACE_WITH_REDIS_PASSWORD"}
############### General ENV VARS #################
# Define DATASETS env var - default to gist-960-euclidean if not set
export DATASETS=${BENCH_DATASETS:-"gist-960-euclidean"}
export ENGINES=${BENCH_ENGINES:-"redis"}
############### MONGO ENV VARS #################
export MONGO_CONNECTION_STRING=${MONGO_CONNECTION_STRING:-"mongodb+srv://performance:performance@cluster0.1234567.mongodb.net/?retryWrites=true&w=1&appName=vector-db-benchmark&readPreference=primary"}
# extract PORT, HOST from connection string
export MONGO_PORT=$(echo $MONGO_CONNECTION_STRING | sed -E 's|.*:([0-9]+).*|\1|')
export MONGO_HOST=$(echo $MONGO_CONNECTION_STRING | sed -E 's|.*@([^:/]+).*|\1|')
export MONGO_USER=$(echo $MONGO_USER)
export MONGO_AUTH=$(echo $MONGO_PASSWORD)
export MONGO_READ_PREFERENCE=${MONGO_READ_PREFERENCE:-"primary"}
export MONGO_WRITE_CONCERN=${MONGO_WRITE_CONCERN:-"1"}
export EMBEDDING_FIELD_NAME=${EMBEDDING_FIELD_NAME:-"embedding"}
export ATLAS_DB_NAME=${MONGO_DB:-"vector-db"}
export ATLAS_COLLECTION_NAME=${ATLAS_COLLECTION_NAME:-"vector-collection"}
export ATLAS_VECTOR_SEARCH_INDEX_NAME=${ATLAS_VECTOR_SEARCH_INDEX_NAME:-"vector-index"}


#echo variables for debugging
echo "REDIS_PORT: $REDIS_PORT"
echo "REDIS_HOST: $REDIS_HOST"
echo "REDIS_USER: $REDIS_USER"
echo "REDIS_AUTH: $REDIS_AUTH"
echo "DATASETS: $DATASETS"
echo "ENGINES: $ENGINES"
echo "MONGO_CONNECTION_STRING: $MONGO_CONNECTION_STRING"
echo "MONGO_PORT: $MONGO_PORT"
echo "MONGO_HOST: $MONGO_HOST"
echo "MONGO_USER: $MONGO_USER"
echo "MONGO_AUTH: $MONGO_AUTH"

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