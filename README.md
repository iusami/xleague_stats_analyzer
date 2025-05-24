# xleague_stats_analyzer

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

## Run E2E tests
```bash
uv run pytest test/test_e2e.py -v
```

The E2E tests verify the complete pipeline from PDF analysis to final CSV output generation. The tests use sample data in `test/data/` and compare results against expected outputs in `test/data/result/`.

## CI/CD
GitHub Actions automatically runs E2E tests on pull requests and pushes to main/update_code branches when source code, tests, or configuration files are modified.
