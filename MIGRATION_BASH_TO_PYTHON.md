# Bash to Python Migration - Benchmark Scripts

## Overview

The bash scripts `run_bench.sh` and `run_quick.sh` have been converted to Python scripts (`run_bench.py` and `run_quick.py`) with enhanced security and maintainability.

## Changes Made

### ✅ Security Improvements

**Credential Exposure Removed:**
- All sensitive values are now redacted in output:
  - `REDIS_USER: [REDACTED]`
  - `REDIS_AUTH: [REDACTED]`
  - `MONGO_USER: [REDACTED]`
  - `MONGO_AUTH: [REDACTED]`
  - `MONGO_CONNECTION_STRING: [REDACTED]`

**Before (bash):**
```bash
echo "REDIS_AUTH: $REDIS_AUTH"
echo "MONGO_AUTH: $MONGO_AUTH"
echo "MONGO_CONNECTION_STRING: $MONGO_CONNECTION_STRING"
```

**After (Python):**
```python
print("REDIS_AUTH: [REDACTED]")
print("MONGO_AUTH: [REDACTED]")
print("MONGO_CONNECTION_STRING: [REDACTED]")
```

### ✅ Functionality Preserved

All original functionality has been maintained:

1. **Environment Variable Handling:**
   - Same defaults as bash scripts
   - Same variable names
   - Same fallback logic

2. **MongoDB Connection String Parsing:**
   - Extracts `MONGO_HOST`, `MONGO_USER`, `MONGO_AUTH` using regex
   - Identical patterns to bash `sed` commands

3. **Experiment Execution:**
   - Same experiment arrays
   - Same execution order
   - Same command-line arguments to `run.py`

4. **Poetry Virtual Environment:**
   - Detects poetry venv path
   - Environment variables are inherited by subprocesses

## Usage

### run_bench.py

Full benchmark suite with Redis and MongoDB experiments:

```bash
# Direct execution
./run_bench.py

# Or with python
python run_bench.py

# With custom environment variables
REDIS_HOST=my-redis.com MONGO_HOST=my-mongo.com ./run_bench.py
```

**Experiments executed:**
1. `redis-default-simple` (Redis vs MongoDB comparison)
2. `mongodb-default` (Redis vs MongoDB comparison)
3. 12 Redis experiments with varying M and EF_CONSTRUCTION parameters

### run_quick.py

Quick test benchmark with minimal experiments:

```bash
# Direct execution
./run_quick.py

# Or with python
python run_quick.py
```

**Experiments executed:**
1. `redis-quicktest`
2. `mongodb-quicktest`

## Environment Variables

Both scripts support the same environment variables as the bash versions:

### Redis Variables
- `REDIS_DB_PORT` (default: `6739`)
- `REDIS_HOST` (default: `psc.122222.eu-west1-mz.gcp.cloud.rlrcp.com`)
- `REDIS_RW_USER` (default: `default`)
- `REDIS_RW_PASS` (default: `REPLACE_WITH_REDIS_PASSWORD`)

### MongoDB Variables
- `MONGO_CONNECTION_STRING` (default: connection string with placeholder credentials)
- `MONGO_READ_PREFERENCE` (default: `primary`)
- `MONGO_WRITE_CONCERN` (default: `1`)
- `EMBEDDING_FIELD_NAME` (default: `embedding`)
- `MONGO_DB` (default: `vector-db`)
- `ATLAS_COLLECTION_NAME` (default: `vector-collection`)
- `ATLAS_VECTOR_SEARCH_INDEX_NAME` (default: `vector-index`)

### General Variables
- `BENCH_DATASETS` (default: `gist-960-euclidean` for run_bench.py, `random-100-euclidean` for run_quick.py)
- `BENCH_ENGINES` (default: `redis`)

## Implementation Details

### Connection String Parsing

The Python scripts use regex patterns identical to the bash `sed` commands:

```python
# Extract host: sed -E 's|.*@([^:/]+).*|\1|'
MONGO_HOST = extract_from_connection_string(conn_str, r'.*@([^:/]+).*')

# Extract user: sed -E 's|.*://([^:]+):.*|\1|'
MONGO_USER = extract_from_connection_string(conn_str, r'.*://([^:]+):.*')

# Extract password: sed -E 's|.*://[^:]+:([^@]+)@.*|\1|'
MONGO_AUTH = extract_from_connection_string(conn_str, r'.*://[^:]+:([^@]+)@.*')
```

### Error Handling

- Poetry environment detection with error messages
- Subprocess execution with error propagation
- Exit codes preserved from failed experiments

## Benefits of Python Version

1. **Security:** No credential leakage in logs
2. **Portability:** Works on any system with Python 3.6+
3. **Maintainability:** Easier to read and modify than bash
4. **Error Handling:** Better error messages and debugging
5. **Type Safety:** Can add type hints for better IDE support

## Backward Compatibility

The bash scripts (`run_bench.sh` and `run_quick.sh`) are still available and functional. You can use either version depending on your preference.

## Testing

Both scripts have been:
- ✅ Syntax validated with `python3 -m py_compile`
- ✅ Made executable with `chmod +x`
- ✅ Tested for credential redaction
- ✅ Verified for connection string parsing

## Next Steps

Consider:
1. Deprecating the bash scripts after testing the Python versions
2. Adding the bash scripts to `.gitignore` if they contain sensitive defaults
3. Creating a `run_bench.example.py` with placeholder credentials

