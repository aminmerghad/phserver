# Order Service Testing Guide

This directory contains comprehensive tests for the Order Service of the Pharmacy application. The tests are organized into different categories to provide thorough coverage of the functionality.

## Test Categories

1. **Unit Tests** (`unit/`): Test individual components in isolation
   - Domain entity tests
   - Value object tests
   - Logic/validation tests

2. **Integration Tests** (`integration/`): Test interactions between components
   - Service to repository interactions
   - Use case tests with mocked dependencies

3. **API Tests** (`test_order_api.py`): Test the API endpoints
   - End-to-end tests
   - Request/response validation
   - Error handling

## Requirements

Make sure you have the required testing dependencies installed:

```bash
pip install pytest pytest-flask pytest-cov coverage
```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided runner script:

```bash
# Run from project root
python app/services/order_service/tests/run_tests.py
```

Options:
- `--unit`: Run only unit tests
- `--integration`: Run only integration tests
- `--api`: Run only API tests
- `--all`: Run all tests (default if no option specified)
- `--coverage`: Generate coverage data
- `--html-report`: Generate HTML coverage report
- `-v` or `--verbose`: Verbose output

Examples:
```bash
# Run unit tests with verbose output
python app/services/order_service/tests/run_tests.py --unit -v

# Run API tests with coverage
python app/services/order_service/tests/run_tests.py --api --coverage

# Generate HTML coverage report
python app/services/order_service/tests/run_tests.py --html-report
```

### Using pytest Directly

Alternatively, you can use pytest commands directly:

```bash
# Run all tests
pytest app/services/order_service/tests

# Run unit tests
pytest app/services/order_service/tests/unit

# Run integration tests
pytest app/services/order_service/tests/integration

# Run API tests
pytest app/services/order_service/tests/test_order_api.py

# Generate coverage report
pytest app/services/order_service/tests --cov=app.services.order_service --cov-report=html
```

## Test Data Setup

Tests use a combination of:
- In-memory database for unit and integration tests
- Temporary SQLite database for API tests
- Test fixtures to set up and tear down data

For API tests, a test database is created for each test run with:
- Test users
- Sample products
- Inventory entries

## Key Test Features

1. **Isolation**: Each test runs in isolation to prevent test interdependence.
2. **Comprehensive Coverage**: Tests cover both happy paths and error cases.
3. **Clean Setup/Teardown**: Fixtures ensure clean environment for each test.
4. **Real DB Testing**: API tests use a real database rather than mocks.

## Troubleshooting

If tests fail with import errors:
1. Make sure you're running from the project root directory
2. Verify that all dependencies are installed
3. Check that the PYTHONPATH includes the project root

If specific API tests fail:
1. Check if the ORDER service dependencies (like auth or inventory) are properly mocked
2. Verify that the test database is properly set up with required data
3. Inspect auth token generation if authentication-related tests fail 