# Security Audit Report - vector-db-benchmark

| Severity | File | Issue | Description | Suggested Mitigation |
|----------|------|-------|-------------|---------------------|
| **CRITICAL** | `run_bench.sh:27-37` | Credentials logged to stdout | Script echoes `REDIS_AUTH`, `MONGO_AUTH`, and `MONGO_CONNECTION_STRING` (containing password) to console output | Remove or mask sensitive values in echo statements. Use `echo "REDIS_AUTH: [REDACTED]"` instead |
| **CRITICAL** | `run_bench.sh:13` | Hardcoded credentials in default value | Default `MONGO_CONNECTION_STRING` contains `performance:performance` credentials | Remove default credentials; require env var to be set externally |
| **HIGH** | `k8s/secrets.yaml` | Secrets file committed to repo | K8s secrets file with placeholder passwords is tracked in git | Add `k8s/secrets.yaml` to `.gitignore`; use `secrets.yaml.example` template instead |
| **HIGH** | `engine/clients/opensearch/config.py:8` | Hardcoded default password | `OPENSEARCH_PASSWORD` defaults to `"passwd"` | Remove default; require explicit configuration |
| **HIGH** | `engine/clients/pgvector/config.py:6` | Hardcoded default password | `PGVECTOR_PASSWORD` defaults to `"passwd"` | Remove default; require explicit configuration |
| **HIGH** | `engine/clients/mongodb/config.py:6-7` | Hardcoded default credentials | `MONGO_AUTH` and `MONGO_USER` default to `"performance"` | Remove defaults; require explicit configuration |
| **MEDIUM** | `tools/upload_results_postgres.sh:69-72` | Password in command line | `POSTGRES_PASSWORD` passed via command line argument to docker | Use environment variable or mounted secret file instead |
| **MEDIUM** | `benchmark/dataset.py:203` | Unsafe tar extraction | `tarfile.extractall()` without path validation can lead to path traversal attacks | Use `tarfile.extractall()` with `filter='data'` (Python 3.12+) or validate member paths |
| **MEDIUM** | `docker-run.sh:163` | Command injection via eval | `eval $DOCKER_CMD` with user-controlled input could allow command injection | Use array-based command execution instead of eval |
| **MEDIUM** | `tools/run_remote.sh:39` | Remote code execution | Script pipes content directly to remote `bash -x` without validation | Add input validation; consider using ansible or similar tools |
| **LOW** | `engine/clients/opensearch/config.py:16` | SSL verification disabled | `verify_certs: False` disables TLS certificate verification | Enable certificate verification in production; make configurable |
| **LOW** | `Dockerfile:80` | Overly permissive permissions | `chmod -R 777` on `/app/results` and `/app/datasets` | Use more restrictive permissions (e.g., 755 or 775) |
| **LOW** | `.gitignore` | Results not fully ignored | `results/*` pattern may not ignore `results/results/` subdirectory with sensitive data | Use `results/` pattern or verify sensitive data isn't committed |
| **INFO** | `docker-test.sh:41-48` | Credentials in environment | Script checks for `DOCKER_PASSWORD` in environment | Acceptable for CI/CD but document secure handling |

## Summary

- **Critical Issues**: 2 (credential exposure in logs, hardcoded credentials)
- **High Issues**: 4 (secrets in repo, hardcoded passwords)
- **Medium Issues**: 4 (command injection, unsafe extraction, password exposure)
- **Low Issues**: 3 (SSL, permissions, gitignore)

## Priority Actions

1. **Immediately** remove credential echoing from `run_bench.sh`
2. **Immediately** add `k8s/secrets.yaml` to `.gitignore` and create a template file
3. Remove all hardcoded default passwords from config files
4. Fix the unsafe `tarfile.extractall()` call

