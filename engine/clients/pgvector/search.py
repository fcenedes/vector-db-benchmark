import multiprocessing as mp
from typing import List, Tuple

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from engine.base_client.distances import Distance
from engine.base_client.search import BaseSearcher
from engine.clients.pgvector.config import (
    get_db_config,
    PGVECTOR_MAX_PARALLEL_WORKERS_PER_GATHER,
    PGVECTOR_PARALLEL_TUPLE_COST,
    PGVECTOR_PARALLEL_SETUP_COST,
    PGVECTOR_MIN_PARALLEL_TABLE_SCAN_SIZE,
    PGVECTOR_FORCE_PARALLEL_MODE,
    PGVECTOR_WORK_MEM,
)
from engine.clients.pgvector.parser import PgVectorConditionParser


class PgvectorSearcher(BaseSearcher):
    conn = None
    cur = None
    distance = None
    search_params = {}
    parser = PgVectorConditionParser()

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        cls.conn = psycopg.connect(**get_db_config(host, connection_params))
        register_vector(cls.conn)
        cls.cur = cls.conn.cursor()
        cls.distance = distance
        cls.search_params = search_params["search_params"]

        # For FLAT searches, optimize for parallel execution
        if "force_flat" in cls.search_params and cls.search_params["force_flat"]:
            # Note: We don't disable indexes globally since:
            # 1. No vector index exists in FLAT mode (not created)
            # 2. PostgreSQL will naturally do sequential scan for vector queries
            # 3. Other indexes (for filtering, etc.) remain useful

            # Configurable parallel execution settings for FLAT searches
            # Priority: Environment variables (from config) > search_params > defaults
            parallel_workers = cls.search_params.get("max_parallel_workers_per_gather", PGVECTOR_MAX_PARALLEL_WORKERS_PER_GATHER)
            parallel_tuple_cost = cls.search_params.get("parallel_tuple_cost", PGVECTOR_PARALLEL_TUPLE_COST)
            parallel_setup_cost = cls.search_params.get("parallel_setup_cost", PGVECTOR_PARALLEL_SETUP_COST)
            min_parallel_size = cls.search_params.get("min_parallel_table_scan_size", PGVECTOR_MIN_PARALLEL_TABLE_SCAN_SIZE)
            force_parallel = cls.search_params.get("force_parallel_mode", PGVECTOR_FORCE_PARALLEL_MODE)
            work_mem = cls.search_params.get("work_mem", PGVECTOR_WORK_MEM)

            cls.cur.execute(f"SET max_parallel_workers_per_gather = {parallel_workers}")
            cls.cur.execute(f"SET parallel_tuple_cost = {parallel_tuple_cost}")
            cls.cur.execute(f"SET parallel_setup_cost = {parallel_setup_cost}")
            cls.cur.execute(f"SET min_parallel_table_scan_size = '{min_parallel_size}'")
            cls.cur.execute(f"SET force_parallel_mode = {force_parallel}")
            cls.cur.execute(f"SET work_mem = '{work_mem}'")

    @classmethod
    def search_one(cls, vector, meta_conditions, top) -> List[Tuple[int, float]]:
        # Set HNSW ef_search parameter only if using HNSW index
        if "hnsw_ef" in cls.search_params:
            cls.cur.execute(f"SET hnsw.ef_search = {cls.search_params['hnsw_ef']}")

        # Ensure vector is in the correct format for pgvector
        try:
            if isinstance(vector, bytes):
                # If vector is bytes, it might be serialized - try to convert
                # First try to interpret as float32 bytes
                try:
                    import struct
                    num_floats = len(vector) // 4  # 4 bytes per float32
                    vector_array = np.array(struct.unpack(f'{num_floats}f', vector), dtype=np.float32)
                except struct.error:
                    # If that fails, try to decode as numpy array
                    vector_array = np.frombuffer(vector, dtype=np.float32)
            elif isinstance(vector, np.ndarray):
                vector_array = vector.astype(np.float32)
            else:
                # Convert list to numpy array
                vector_array = np.array(vector, dtype=np.float32)
        except Exception as e:
            raise ValueError(f"Failed to convert vector to proper format. Vector type: {type(vector)}, Error: {e}")

        if cls.distance == Distance.COSINE:
            query = f"SELECT id, embedding <=> %s AS _score FROM items ORDER BY _score LIMIT {top};"
        elif cls.distance == Distance.L2:
            query = f"SELECT id, embedding <-> %s AS _score FROM items ORDER BY _score LIMIT {top};"
        else:
            raise NotImplementedError(f"Unsupported distance metric {cls.distance}")

        cls.cur.execute(
            query,
            (vector_array,),
        )
        return cls.cur.fetchall()

    @classmethod
    def delete_client(cls):
        if cls.cur:
            cls.cur.close()
            cls.conn.close()
