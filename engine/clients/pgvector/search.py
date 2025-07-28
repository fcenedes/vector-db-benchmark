import multiprocessing as mp
from typing import List, Tuple

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from engine.base_client.distances import Distance
from engine.base_client.search import BaseSearcher
from engine.clients.pgvector.config import get_db_config
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

        # For FLAT searches, disable index usage to force full scan
        if "force_flat" in cls.search_params and cls.search_params["force_flat"]:
            cls.cur.execute("SET enable_indexscan = off")
            cls.cur.execute("SET enable_bitmapscan = off")

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
            # Reset index settings if they were disabled for FLAT searches
            if "force_flat" in cls.search_params and cls.search_params["force_flat"]:
                try:
                    cls.cur.execute("SET enable_indexscan = on")
                    cls.cur.execute("SET enable_bitmapscan = on")
                except:
                    pass  # Connection might be closed already
            cls.cur.close()
            cls.conn.close()
