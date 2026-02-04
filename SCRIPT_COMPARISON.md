# Bash vs Python Script Comparison

## Side-by-Side Comparison

### Credential Handling

| Aspect | Bash (run_bench.sh) | Python (run_bench.py) |
|--------|---------------------|----------------------|
| **REDIS_AUTH output** | `echo "REDIS_AUTH: $REDIS_AUTH"` | `print("REDIS_AUTH: [REDACTED]")` |
| **MONGO_AUTH output** | `echo "MONGO_AUTH: $MONGO_AUTH"` | `print("MONGO_AUTH: [REDACTED]")` |
| **MONGO_USER output** | `echo "MONGO_USER: $MONGO_USER"` | `print("MONGO_USER: [REDACTED]")` |
| **Connection string** | `echo "MONGO_CONNECTION_STRING: $MONGO_CONNECTION_STRING"` | `print("MONGO_CONNECTION_STRING: [REDACTED]")` |
| **Security Risk** | ❌ HIGH - Credentials in logs | ✅ LOW - Credentials redacted |

### Connection String Parsing

| Operation | Bash | Python |
|-----------|------|--------|
| **Extract Host** | `sed -E 's\|.*@([^:/]+).*\|\1\|'` | `re.search(r'.*@([^:/]+).*', conn_str)` |
| **Extract User** | `sed -E 's\|.*://([^:]+):.*\|\1\|'` | `re.search(r'.*://([^:]+):.*', conn_str)` |
| **Extract Password** | `sed -E 's\|.*://[^:]+:([^@]+)@.*\|\1\|'` | `re.search(r'.*://[^:]+:([^@]+)@.*', conn_str)` |
| **Readability** | ⚠️ Medium - Regex in shell | ✅ High - Clear function |

### Environment Activation

| Aspect | Bash | Python |
|--------|------|--------|
| **Poetry venv** | `. $(poetry env info --path)/bin/activate` | `subprocess.run(["poetry", "env", "info", "--path"])` |
| **Approach** | Source activation script | Get path, inherit environment |
| **Error Handling** | None | Try/except with error message |

### Experiment Execution

| Aspect | Bash | Python |
|--------|------|--------|
| **Loop syntax** | `for experiment in "${experiments_redis[@]}"` | `for experiment in experiments_redis:` |
| **Command execution** | `python run.py --engines "$experiment"` | `subprocess.run(["python", "run.py", "--engines", experiment])` |
| **Error handling** | None (continues on error) | Exits on error with message |
| **Progress output** | `echo` statements | `print()` statements |

## Feature Comparison

| Feature | run_bench.sh | run_bench.py | Status |
|---------|--------------|--------------|--------|
| Redis environment variables | ✅ | ✅ | Identical |
| MongoDB environment variables | ✅ | ✅ | Identical |
| Connection string parsing | ✅ | ✅ | Identical logic |
| Poetry venv activation | ✅ | ✅ | Different approach, same result |
| Redis-default-simple experiment | ✅ | ✅ | Identical |
| MongoDB-default experiment | ✅ | ✅ | Identical |
| 12 Redis experiments | ✅ | ✅ | Identical |
| Credential redaction | ❌ | ✅ | **NEW** |
| Error handling | ❌ | ✅ | **IMPROVED** |
| Type safety | ❌ | ⚠️ (can add) | **IMPROVED** |

## Quick Test Comparison

| Feature | run_quick.sh | run_quick.py | Status |
|---------|--------------|--------------|--------|
| Default dataset | `random-100-euclidean` | `random-100-euclidean` | Identical |
| Redis quicktest | ✅ | ✅ | Identical |
| MongoDB quicktest | ✅ | ✅ | Identical |
| Credential redaction | ❌ | ✅ | **NEW** |

## Code Quality Metrics

| Metric | Bash | Python |
|--------|------|--------|
| **Lines of code** | 82 (run_bench.sh) | 155 (run_bench.py) |
| **Readability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Error messages** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Security** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Portability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Migration Checklist

- [x] Convert environment variable handling
- [x] Convert connection string parsing
- [x] Convert experiment arrays
- [x] Convert experiment execution loops
- [x] Add credential redaction
- [x] Add error handling
- [x] Make scripts executable
- [x] Test syntax validation
- [x] Document changes
- [ ] Test in production environment
- [ ] Deprecate bash scripts (optional)

## Recommendations

1. **Use Python scripts for production** - Better security and error handling
2. **Keep bash scripts as backup** - During transition period
3. **Test both versions** - Ensure identical behavior
4. **Update CI/CD** - Switch to Python scripts
5. **Document in README** - Update usage instructions

## Example Output Comparison

### Bash Output (INSECURE)
```
REDIS_AUTH: my-secret-password-123
MONGO_AUTH: another-secret-456
MONGO_CONNECTION_STRING: mongodb+srv://user:password@host/...
```

### Python Output (SECURE)
```
REDIS_AUTH: [REDACTED]
MONGO_AUTH: [REDACTED]
MONGO_CONNECTION_STRING: [REDACTED]
```

## Performance

Both scripts have similar performance:
- Python has ~50ms startup overhead
- Negligible compared to benchmark runtime (minutes to hours)
- No measurable difference in practice

