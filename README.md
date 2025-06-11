# API Tests for Barrel Monitor

## Dependency Installation

```bash
pip install -r requirements.txt
```

## Environment Setup

To change the target API URL, edit the value in:

```
configurations.py

TESTENV_URL = "https://to-barrel-monitor.azurewebsites.net"
```

## Running Tests

### Standard execution

```bash
pytest -v
```

### Parallel execution (e.g. 4 parallel workers)

```bash
pip install pytest-xdist
pytest -n 4
```

Tests are independent and safe to run in parallel.
