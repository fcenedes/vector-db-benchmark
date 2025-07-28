import pgvector.psycopg
import psycopg

from benchmark.dataset import Dataset
from engine.base_client import IncompatibilityError
from engine.base_client.configure import BaseConfigurator
from engine.base_client.distances import Distance
from engine.clients.pgvector.config import get_db_config


class PgvectorConfigurator(BaseConfigurator):
    DISTANCE_MAPPING = {
        Distance.L2: "vector_l2_ops",
        Distance.COSINE: "vector_cosine_ops",
    }

    def __init__(self, host, collection_params: dict, connection_params: dict):
        super().__init__(host, collection_params, connection_params)
        self.conn = psycopg.connect(**get_db_config(host, connection_params))
        print("configure connection created")
        self.conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        pgvector.psycopg.register_vector(self.conn)

    def clean(self):
        self.conn.execute(
            "DROP TABLE IF EXISTS items CASCADE;",
        )

    def recreate(self, dataset: Dataset, collection_params):
        if dataset.config.distance == Distance.DOT:
            raise IncompatibilityError

        self.conn.execute(
            f"""CREATE TABLE items (
                id SERIAL PRIMARY KEY,
                embedding vector({dataset.config.vector_size}) NOT NULL
            );"""
        )
        self.conn.execute("ALTER TABLE items ALTER COLUMN embedding SET STORAGE PLAIN")

        try:
            distance_type = self.DISTANCE_MAPPING[dataset.config.distance]
        except KeyError:
            raise IncompatibilityError(
                f"Unsupported distance metric: {dataset.config.distance}"
            )

        # Check if we should create HNSW index or use FLAT (no index for full scan)
        if "hnsw_config" in collection_params:
            # Auto-detect core count and set parallel workers for faster index builds (pgvector 0.7.0+)
            max_parallel_workers = collection_params['hnsw_config'].get('max_parallel_workers', 'auto')

            if max_parallel_workers == 'auto':
                # Try to get actual CPU core count from PostgreSQL
                try:
                    # Get max_worker_processes setting as baseline
                    worker_result = self.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_worker_processes'").fetchone()
                    available_workers = int(worker_result[0]) if worker_result else 8

                    # Try to get actual CPU cores if available (PostgreSQL 13+)
                    try:
                        cpu_cores_result = self.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_parallel_workers'").fetchone()
                        if cpu_cores_result:
                            available_workers = min(available_workers, int(cpu_cores_result[0]))
                    except:
                        pass  # Fallback to max_worker_processes

                    # Use AWS recommendation: total cores - 2 (but at least 1)
                    max_parallel_workers = max(1, available_workers - 2)
                    print(f"Auto-detected {available_workers} worker processes, using {max_parallel_workers} parallel workers")

                except Exception as e:
                    print(f"Failed to auto-detect workers, using default of 4: {e}")
                    max_parallel_workers = 8

            if max_parallel_workers > 0:
                self.conn.execute(f"SET max_parallel_workers = {max_parallel_workers}")
                self.conn.execute(f"SET max_parallel_workers_per_gather = {max_parallel_workers}")
                self.conn.execute(f"SET max_parallel_maintenance_workers = {max_parallel_workers}")

            # Create HNSW index with optimized parameters
            self.conn.execute(
                f"CREATE INDEX on items USING hnsw(embedding {distance_type}) WITH (m = {collection_params['hnsw_config']['m']}, ef_construction = {collection_params['hnsw_config']['ef_construct']})"
            )
        elif "flat_config" in collection_params:
            # For FLAT, configure parallel workers for faster query execution during full scans
            max_parallel_workers = collection_params['flat_config'].get('max_parallel_workers', 'auto')

            if max_parallel_workers == 'auto':
                # Try to get actual CPU core count from PostgreSQL
                try:
                    # Get max_worker_processes setting as baseline
                    worker_result = self.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_worker_processes'").fetchone()
                    available_workers = int(worker_result[0]) if worker_result else 8

                    # Try to get actual CPU cores if available (PostgreSQL 13+)
                    try:
                        cpu_cores_result = self.conn.execute("SELECT setting FROM pg_settings WHERE name = 'max_parallel_workers'").fetchone()
                        if cpu_cores_result:
                            available_workers = min(available_workers, int(cpu_cores_result[0]))
                    except:
                        pass  # Fallback to max_worker_processes

                    # Use AWS recommendation: total cores - 2 (but at least 1)
                    max_parallel_workers = max(1, available_workers - 2)
                    print(f"Auto-detected {available_workers} worker processes, using {max_parallel_workers} parallel workers for FLAT queries")

                except Exception as e:
                    print(f"Failed to auto-detect workers for FLAT, using default of 8: {e}")
                    max_parallel_workers = 8

            if max_parallel_workers > 0:
                self.conn.execute(f"SET max_parallel_workers = {max_parallel_workers}")
                self.conn.execute(f"SET max_parallel_workers_per_gather = {max_parallel_workers}")
                # For FLAT, we don't create any index - PostgreSQL will do a full table scan with parallel workers

        self.conn.close()

    def delete_client(self):
        self.conn.close()
