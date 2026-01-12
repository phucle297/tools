# Test Suite for report-bot

## Overview

Comprehensive test suite for the report-bot project with 128 tests covering all core modules.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_cli.py         # Basic CLI integration tests
└── unit/                    # Unit tests
    ├── __init__.py
    ├── test_categorizer.py  # Commit categorization tests (13 tests)
    ├── test_commits.py      # Git operations tests (31 tests)
    ├── test_dates.py        # Date range utilities tests (24 tests)
    ├── test_exporters.py    # Export functionality tests (24 tests)
    ├── test_stats.py        # Git statistics tests (11 tests)
    ├── test_summarizer.py   # AI summarization tests (10 tests)
    └── test_tickets.py      # Ticket extraction tests (13 tests)
```

## Test Coverage

- **Total Tests:** 128
- **All Passing:** ✓ 128/128 
- **Code Coverage:** 46% overall
  - `report/git/commits.py`: 94%
  - `report/utils/categorizer.py`: 100%
  - `report/utils/dates.py`: 100%
  - `report/utils/exporters.py`: 95%
  - `report/utils/stats.py`: 89%
  - `report/utils/tickets.py`: 100%
  - `report/ai/summarizer.py`: 98%

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=report --cov-report=html --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/unit/test_commits.py -v
```

### Run specific test class
```bash
pytest tests/unit/test_commits.py::TestGetCommits -v
```

### Run specific test
```bash
pytest tests/unit/test_commits.py::TestGetCommits::test_get_commits_returns_messages -v
```

### Run only unit tests
```bash
pytest tests/unit/ -v
```

### Run only integration tests
```bash
pytest tests/integration/ -v
```

## Test Modules

### Unit Tests

#### `test_commits.py` (31 tests)
Tests for git repository operations:
- CommitInfo data structure
- Getting commits with filtering
- Detailed commit information
- Author filtering (including "me" keyword)
- Multi-repository support
- Repository discovery

#### `test_dates.py` (24 tests)
Tests for date range utilities:
- Today/yesterday ranges
- This week/last week ranges
- Custom date ranges
- Last N days
- Month ranges
- Date validation

#### `test_categorizer.py` (13 tests)
Tests for commit categorization:
- Console/Server/Others categorization
- Keyword matching
- Case insensitivity
- Grouping commits by component

#### `test_exporters.py` (24 tests)
Tests for export functionality:
- JSON export
- Markdown export
- HTML export
- Email-friendly HTML export
- Metadata handling
- Grouped commit exports

#### `test_stats.py` (11 tests)
Tests for git statistics:
- Author statistics
- Repository statistics
- Line counts (insertions/deletions)
- Files changed tracking
- Author filtering

#### `test_tickets.py` (13 tests)
Tests for ticket extraction:
- JIRA ticket patterns
- GitHub issue patterns
- Linear ticket patterns
- Custom patterns
- Grouping by ticket
- Formatting summaries

#### `test_summarizer.py` (10 tests)
Tests for AI summarization:
- API initialization
- Successful summarization
- Error handling
- SSL verification
- Grouped commits
- Empty commits handling

### Integration Tests

#### `test_cli.py` (2 tests)
Basic CLI integration tests:
- CLI module import
- Command registration

## Fixtures

### `temp_git_repo`
Creates a temporary git repository with initial configuration for testing.

### `populated_git_repo`
Creates a git repository with multiple commits over a 7-day period.

### `sample_commits`
Provides sample CommitInfo objects for testing without git operations.

### `mock_env_vars`
Allows setting environment variables for tests.

## Test Dependencies

```
pytest>=7.0          # Testing framework
pytest-cov>=4.0      # Coverage plugin
pytest-mock>=3.10    # Mocking utilities
```

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=report --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Writing New Tests

### Test Structure Template

```python
"""Tests for report.module.submodule"""
import pytest

from report.module.submodule import function_to_test


class TestFunctionName:
    """Test function_to_test function"""
    
    def test_basic_functionality(self):
        """Test basic use case"""
        result = function_to_test(input_data)
        assert result == expected_output
    
    def test_edge_case(self):
        """Test edge case handling"""
        # Test implementation
        pass
    
    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            function_to_test(invalid_input)
```

### Best Practices

1. **Use descriptive test names**: Test names should clearly indicate what is being tested
2. **One assertion per test**: Keep tests focused on a single behavior
3. **Use fixtures**: Leverage pytest fixtures for setup and teardown
4. **Mock external dependencies**: Use mocking for API calls, file I/O, etc.
5. **Test edge cases**: Don't just test the happy path
6. **Keep tests independent**: Tests should not depend on each other

## Troubleshooting

### Tests fail with "Not a git repository"
Ensure you're using the `temp_git_repo` or `populated_git_repo` fixtures.

### SSL errors in summarizer tests
Check that requests exceptions are properly mocked.

### Date-related test failures
Tests use datetime.now() which may cause issues near midnight. Fixtures handle this appropriately.

## Future Improvements

- [ ] Add integration tests for CLI commands
- [ ] Increase coverage for CLI modules
- [ ] Add performance tests
- [ ] Add tests for config management
- [ ] Mock git operations for faster tests
- [ ] Add property-based testing with hypothesis

## Coverage Report

View detailed coverage report:
```bash
pytest tests/ --cov=report --cov-report=html
# Open htmlcov/index.html in browser
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Follow existing test patterns
