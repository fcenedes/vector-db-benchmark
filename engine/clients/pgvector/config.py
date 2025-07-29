import os

PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", 5432))
PGVECTOR_DB = os.getenv("PGVECTOR_DB", "postgres")
PGVECTOR_USER = os.getenv("PGVECTOR_USER", "postgres")
PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD", "passwd")

# Parallel execution settings
PGVECTOR_MAX_PARALLEL_WORKERS_PER_GATHER = int(os.getenv("PGVECTOR_MAX_PARALLEL_WORKERS_PER_GATHER", 8))
PGVECTOR_PARALLEL_TUPLE_COST = float(os.getenv("PGVECTOR_PARALLEL_TUPLE_COST", 0.01))
PGVECTOR_PARALLEL_SETUP_COST = int(os.getenv("PGVECTOR_PARALLEL_SETUP_COST", 100))
PGVECTOR_MIN_PARALLEL_TABLE_SCAN_SIZE = os.getenv("PGVECTOR_MIN_PARALLEL_TABLE_SCAN_SIZE", "1MB")
PGVECTOR_FORCE_PARALLEL_MODE = os.getenv("PGVECTOR_FORCE_PARALLEL_MODE", "on")
PGVECTOR_WORK_MEM = os.getenv("PGVECTOR_WORK_MEM", "4GB")


def get_db_config(host, connection_params):
    return {
        "host": host or "localhost",
        "port": PGVECTOR_PORT,
        "dbname": PGVECTOR_DB,
        "user": PGVECTOR_USER,
        "password": PGVECTOR_PASSWORD,
        "autocommit": True,
        **connection_params,
    }
