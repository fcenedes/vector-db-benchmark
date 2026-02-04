#!/bin/bash

############### Redis ENV VARS #################
export REDIS_PORT=${REDIS_DB_PORT:-6739}
export REDIS_HOST=${REDIS_HOST:-"psc.122222.eu-west1-mz.gcp.cloud.rlrcp.com"}
export REDIS_USER=${REDIS_RW_USER:-"default"}
export REDIS_AUTH=${REDIS_RW_PASS:-"REPLACE_WITH_REDIS_PASSWORD"}
############### General ENV VARS #################
# Define DATASETS env var - default to gist-960-euclidean if not set
export DATASETS=${BENCH_DATASETS:-"random-100-euclidean"}
export ENGINES=${BENCH_ENGINES:-"redis"}
############### MONGO ENV VARS #################
export MONGO_CONNECTION_STRING=${MONGO_CONNECTION_STRING:-"mongodb+srv://performance:performance@cluster0.1234567.mongodb.net/?retryWrites=true&w=1&appName=vector-db-benchmark&readPreference=primary"}
# extract HOST, USER, AUTH from connection string
export MONGO_HOST=$(echo $MONGO_CONNECTION_STRING | sed -E 's|.*@([^:/]+).*|\1|')
export MONGO_USER=$(echo $MONGO_CONNECTION_STRING | sed -E 's|.*://([^:]+):.*|\1|')
export MONGO_AUTH=$(echo $MONGO_CONNECTION_STRING | sed -E 's|.*://[^:]+:([^@]+)@.*|\1|')
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
# Define experiments array for redis
echo "-----------------------------------"
echo "Running experiment: redis-quicktest - Redis VS MongoDB - Default"
python run.py --engines "redis-quicktest" --datasets "${DATASETS}" --host "${REDIS_HOST}"
echo "Completed experiment: redis-quicktest"
echo "-----------------------------------"
echo "Running experiment: mongodb-quicktest - Redis VS MongoDB - Default"
python run.py --engines "mongodb-quicktest" --datasets "${DATASETS}" --host "${MONGO_HOST}"
echo "Completed experiment: mongodb-quicktest"
echo "-----------------------------------"
echo "Redis VS MongoDB - Default completed!"

echo "All experiments completed!"