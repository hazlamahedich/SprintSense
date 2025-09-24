# Test Cycle Automation Framework

An automated testing framework for running Playwright E2E tests with smart retries, failure analysis, and comprehensive reporting.

## Features

- Automated test execution with smart retry logic
- Failure analysis and categorization
- Comprehensive HTML reporting with charts
- Test artifact collection (traces, screenshots, videos)
- Resource management with cooldown periods
- Support for multiple browsers (Chrome, Firefox, Safari)

## Installation

```bash
# Install the package using Poetry
poetry install

# Install browsers for Playwright
poetry run playwright install
```

## Usage

### Basic Usage

Run the test cycle with default settings:

```bash
poetry run test-cycle
```

Or specify a custom test directory:

```bash
poetry run test-cycle /path/to/tests
```

### Environment Variables

- `TEST_DIR`: Path to the test directory (default: ./tests/e2e)
- `PLAYWRIGHT_BROWSERS_PATH`: Custom path for browser installations
- `DEBUG`: Set to '1' for debug logging

## Configuration

The framework uses several configuration parameters that can be customized:

- Maximum retry attempts: 3 (default)
- Cooldown period between retries: 5 seconds
- Browser configurations from playwright.config.ts
- Resource management rules

## Test Results

After running the tests, you'll find:

1. HTML Report (`test-reports/report.html`):
   - Test execution summary
   - Failure analysis with charts
   - Retry statistics
   - Links to artifacts

2. JSON Data (`test-reports/report.json`):
   - Machine-readable test results
   - Analysis data
   - Failure patterns

3. Artifacts (`test-results/`):
   - Screenshots of failures
   - Trace files
   - Video recordings
   - Browser logs

## Error Categories

The framework categorizes test failures into:

- Selector issues (element not found, visibility problems)
- Timeout issues (slow loading, performance problems)
- Network issues (API failures, connection problems)
- Assertion issues (unexpected values, state mismatches)

## Integration

### With Existing Playwright Setup

The framework integrates with your existing Playwright configuration:

1. Uses your `playwright.config.ts` settings
2. Respects browser configurations
3. Maintains existing test structure
4. Preserves custom test fixtures

### With CI/CD

Example GitHub Actions workflow:

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'

      - name: Install Poetry
        run: curl -sSL https://install.python-poetry.org | python3 -

      - name: Install dependencies
        run: poetry install

      - name: Install browsers
        run: poetry run playwright install

      - name: Run tests
        run: poetry run test-cycle

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            test-reports/
            test-results/
```

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `poetry run pytest`
5. Submit a pull request

### Code Style

- Python code is formatted with Black
- Linting with Pylint
- Type hints required for public APIs

## License

MIT License
