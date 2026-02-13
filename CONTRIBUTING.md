# Contributing to LazzyORM

Thank you for your interest in contributing to LazzyORM! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Python version**
- **LazzyORM version**
- **MySQL version**
- **Code samples** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement needed?
- **Proposed solution**
- **Alternative solutions** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**
3. **Add tests** for any new functionality
4. **Ensure tests pass**: `pytest tests/`
5. **Format code**: `black lazzy_orm/`
6. **Check linting**: `flake8 lazzy_orm/`
7. **Update documentation** if needed
8. **Commit with clear messages**
9. **Push to your fork**
10. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/LazzyORM.git
cd LazzyORM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/ -v

# Format code
black lazzy_orm/

# Check linting
flake8 lazzy_orm/

# Type checking
mypy lazzy_orm/
```

### Coding Standards

- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Write **docstrings** for all public APIs
- Keep functions **small and focused**
- Add **tests** for new features
- Maintain **backwards compatibility** when possible

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests
- Keep first line under 50 characters
- Add detailed description after blank line if needed

Example:
```
Add LazyUpdate class for UPDATE operations

- Implement parameterized queries for security
- Add support for multiple WHERE conditions
- Include comprehensive error handling
- Add unit tests

Fixes #123
```

### Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage (>80%)
- Test edge cases and error conditions

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=lazzy_orm --cov-report=html

# Run specific test file
pytest tests/test_lazy_query.py -v
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Include code examples in docstrings
- Update CHANGELOG for significant changes

## Project Structure

```
LazzyORM/
├── lazzy_orm/           # Main package
│   ├── config/          # Database configuration
│   ├── lazzy_fetch/     # Fetch operations
│   ├── lazzy_insert/    # Insert operations
│   ├── lazzy_query/     # Query building
│   ├── lazzy_update/    # Update operations
│   ├── lazzy_delete/    # Delete operations
│   ├── logger/          # Logging utilities
│   └── exceptions.py    # Custom exceptions
├── tests/               # Test suite
├── docs/                # Documentation
├── Readme.md            # Main documentation
├── setup.py             # Package setup
└── pyproject.toml       # Project configuration
```

## Release Process

1. Update version in `setup.py`, `pyproject.toml`, and `lazzy_orm/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag
5. Build and upload to PyPI

## Questions?

Feel free to open an issue for any questions or concerns!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
