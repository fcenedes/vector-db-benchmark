from typing import List, Optional

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from engine.base_client.upload import BaseUploader
from engine.clients.pgvector.config import get_db_config


class PgVectorUploader(BaseUploader):
    conn = None
    cur = None
    upload_params = {}

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        cls.conn = psycopg.connect(**get_db_config(host, connection_params))
        register_vector(cls.conn)
        cls.cur = cls.conn.cursor()
        cls.upload_params = upload_params

        # Auto-detect core count for parallel maintenance workers
        try:
            # Get max_worker_processes setting as baseline
            worker_result = cls.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_worker_processes'").fetchone()
            available_workers = int(worker_result[0]) if worker_result else 8

            # Try to get actual CPU cores if available (PostgreSQL 13+)
            try:
                cpu_cores_result = cls.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_parallel_workers'").fetchone()
                if cpu_cores_result:
                    available_workers = min(available_workers, int(cpu_cores_result[0]))
            except:
                pass  # Fallback to max_worker_processes

            # Use AWS recommendation: total cores - 2 (but at least 1, max 16 for maintenance)
            max_maintenance_workers = min(16, max(1, available_workers - 2))
            print(f"Auto-detected {available_workers} worker processes, using {max_maintenance_workers} parallel maintenance workers for uploads")

        except Exception as e:
            print(f"Failed to auto-detect workers for uploads, using default of 8: {e}")
            max_maintenance_workers = 8

        # Optimize memory settings for large uploads based on AWS recommendations
        cls.conn.execute("SET maintenance_work_mem = '2GB'")
        cls.conn.execute(f"SET max_parallel_maintenance_workers = {max_maintenance_workers}")

    @classmethod
    def upload_batch(
        cls, ids: List[int], vectors: List[list], metadata: Optional[List[dict]]
    ):
        vectors = np.array(vectors)

        # Copy is faster than insert
        with cls.cur.copy("COPY items (id, embedding) FROM STDIN") as copy:
            for i, embedding in zip(ids, vectors):
                copy.write_row((i, embedding))

    @classmethod
    def delete_client(cls):
        if cls.cur:
            cls.cur.close()
            cls.conn.close()
