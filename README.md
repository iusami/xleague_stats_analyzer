# xleague_stats_analyzer

[![Tests and Coverage](https://github.com/ippeiusami/xleague_stats_analyzer/actions/workflows/tests-and-coverage.yml/badge.svg)](https://github.com/ippeiusami/xleague_stats_analyzer/actions/workflows/tests-and-coverage.yml)
[![Coverage](https://img.shields.io/badge/coverage-check%20latest%20run-blue)](https://github.com/ippeiusami/xleague_stats_analyzer/actions/workflows/tests-and-coverage.yml)

# prerequisites
- install [uv](https://github.com/astral-sh/uv)

# How to use

## Single PDF analysis
```bash
uv run src/main.py path_to_stats.pdf
```

## Multiple PDF analysis
```bash
uv run src/main_multi.py pdf_directory config.json output_directory
```

## Data summarization
```bash
uv run src/summarize_data.py output_directory result_directory
```

## Full pipeline example
```bash
# Step 1: Analyze PDFs
uv run src/main_multi.py test/data config.json test/output

# Step 2: Summarize results
uv run src/summarize_data.py test/output/ test/data/result
```

# Testing

## Run unit tests with coverage
```bash
# Run all tests with coverage
uv run pytest src/tests/ -v --cov=src --cov-report=term-missing

# Run specific test files
uv run pytest src/tests/test_models.py -v
uv run pytest src/tests/test_utils.py -v
uv run pytest src/tests/test_logger.py -v
```

## Run E2E tests
```bash
uv run pytest test/test_e2e.py -v
```

The E2E tests verify the complete pipeline from PDF analysis to final CSV output generation. The tests use sample data in `test/data/` and compare results against expected outputs in `test/data/result/`.

## Run all tests
```bash
# Run both unit tests and E2E tests with coverage
uv run pytest -v --cov=src --cov-report=term-missing --cov-report=html
```

## Coverage reports
- **Terminal**: Coverage summary displayed in terminal
- **HTML**: Detailed coverage report in `htmlcov/index.html`
- **XML**: Coverage data in `coverage.xml` for CI/CD integration

## CI/CD
GitHub Actions automatically runs both unit tests and E2E tests with coverage reporting on pull requests and pushes to main/update_code branches. Coverage badges are automatically updated and PR comments show coverage statistics.

### Test Structure
```
src/tests/          # Unit tests
├── test_models.py  # Model classes tests
├── test_utils.py   # Utility functions tests
└── test_logger.py  # Logger functionality tests

test/               # Integration tests
└── test_e2e.py     # End-to-end pipeline tests
```
