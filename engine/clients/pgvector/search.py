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

        if cls.distance == Distance.COSINE:
            query = f"SELECT id, embedding <=> %s AS _score FROM items ORDER BY _score LIMIT {top};"
        elif cls.distance == Distance.L2:
            query = f"SELECT id, embedding <-> %s AS _score FROM items ORDER BY _score LIMIT {top};"
        else:
            raise NotImplementedError(f"Unsupported distance metric {cls.distance}")

        cls.cur.execute(
            query,
            (np.array(vector),),
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
