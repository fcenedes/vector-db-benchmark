#!/usr/bin/env python3
"""
Benchmark runner script - Python version of run_bench.sh
Executes Redis and MongoDB benchmarks with various configurations.
"""

import os
import re
import subprocess
import sys


def extract_from_connection_string(connection_string, pattern):
    """Extract a component from MongoDB connection string using regex."""
    match = re.search(pattern, connection_string)
    return match.group(1) if match else ""


def get_poetry_venv_path():
    """Get the poetry virtual environment path."""
    try:
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting poetry environment: {e}", file=sys.stderr)
        sys.exit(1)


def run_experiment(experiment_name, dataset, host, description=""):
    """Run a single benchmark experiment."""
    print("-----------------------------------")
    if description:
        print(f"Running experiment: {experiment_name} - {description}")
    else:
        print(f"Running experiment: {experiment_name}")
    
    cmd = ["python", "run.py", "--engines", experiment_name, "--datasets", dataset, "--host", host]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Completed experiment: {experiment_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running experiment {experiment_name}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("-----------------------------------")


def main():
    # ============== Redis ENV VARS ==============
    os.environ["REDIS_PORT"] = os.getenv("REDIS_DB_PORT", "6739")
    os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "psc.122222.eu-west1-mz.gcp.cloud.rlrcp.com")
    os.environ["REDIS_USER"] = os.getenv("REDIS_RW_USER", "default")
    os.environ["REDIS_AUTH"] = os.getenv("REDIS_RW_PASS", "REPLACE_WITH_REDIS_PASSWORD")
    
    # ============== General ENV VARS ==============
    os.environ["DATASETS"] = os.getenv("BENCH_DATASETS", "gist-960-euclidean")
    os.environ["ENGINES"] = os.getenv("BENCH_ENGINES", "redis")
    
    # ============== MONGO ENV VARS ==============
    mongo_connection_string = os.getenv(
        "MONGO_CONNECTION_STRING",
        "mongodb+srv://performance:performance@cluster0.1234567.mongodb.net/?retryWrites=true&w=1&appName=vector-db-benchmark&readPreference=primary"
    )
    os.environ["MONGO_CONNECTION_STRING"] = mongo_connection_string
    
    # Extract HOST, USER, AUTH from connection string
    os.environ["MONGO_HOST"] = extract_from_connection_string(
        mongo_connection_string, r'.*@([^:/]+).*'
    )
    os.environ["MONGO_USER"] = extract_from_connection_string(
        mongo_connection_string, r'.*://([^:]+):.*'
    )
    os.environ["MONGO_AUTH"] = extract_from_connection_string(
        mongo_connection_string, r'.*://[^:]+:([^@]+)@.*'
    )
    
    os.environ["MONGO_READ_PREFERENCE"] = os.getenv("MONGO_READ_PREFERENCE", "primary")
    os.environ["MONGO_WRITE_CONCERN"] = os.getenv("MONGO_WRITE_CONCERN", "1")
    os.environ["EMBEDDING_FIELD_NAME"] = os.getenv("EMBEDDING_FIELD_NAME", "embedding")
    os.environ["ATLAS_DB_NAME"] = os.getenv("MONGO_DB", "vector-db")
    os.environ["ATLAS_COLLECTION_NAME"] = os.getenv("ATLAS_COLLECTION_NAME", "vector-collection")
    os.environ["ATLAS_VECTOR_SEARCH_INDEX_NAME"] = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME", "vector-index")
    
    # Print configuration (with sensitive values redacted)
    print("REDIS_PORT:", os.environ["REDIS_PORT"])
    print("REDIS_HOST:", os.environ["REDIS_HOST"])
    print("REDIS_USER: [REDACTED]")
    print("REDIS_AUTH: [REDACTED]")
    print("DATASETS:", os.environ["DATASETS"])
    print("ENGINES:", os.environ["ENGINES"])
    print("MONGO_CONNECTION_STRING: [REDACTED]")
    print("MONGO_PORT:", os.environ.get("MONGO_PORT", "N/A"))
    print("MONGO_HOST:", os.environ["MONGO_HOST"])
    print("MONGO_USER: [REDACTED]")
    print("MONGO_AUTH: [REDACTED]")
    print()
    
    # Activate poetry virtual environment
    venv_path = get_poetry_venv_path()
    activate_script = os.path.join(venv_path, "bin", "activate")
    
    # Note: We don't need to source activate in Python, just ensure we're using the right Python
    # The subprocess calls will inherit the environment
    
    # Define experiments
    datasets = os.environ["DATASETS"]
    redis_host = os.environ["REDIS_HOST"]
    mongo_host = os.environ["MONGO_HOST"]
    
    # Redis vs MongoDB - Default experiments
    run_experiment("redis-default-simple", datasets, redis_host, "Redis VS MongoDB - Default")
    run_experiment("mongodb-default", datasets, mongo_host, "Redis VS MongoDB - Default")
    
    print("Redis VS MongoDB - Default completed!")
    
    # Redis experiments array
    experiments_redis = [
        "redis-m-16-ef-64",
        "redis-m-16-ef-128",
        "redis-m-16-ef-256",
        "redis-m-16-ef-512",
        "redis-m-32-ef-64",
        "redis-m-32-ef-128",
        "redis-m-32-ef-256",
        "redis-m-32-ef-512",
        "redis-m-64-ef-64",
        "redis-m-64-ef-128",
        "redis-m-64-ef-256",
        "redis-m-64-ef-512",
    ]
    
    # Run Redis experiments
    for experiment in experiments_redis:
        run_experiment(experiment, datasets, redis_host, "Redis")
    
    print("All experiments completed!")


if __name__ == "__main__":
    main()

