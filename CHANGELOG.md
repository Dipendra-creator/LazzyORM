# Changelog

All notable changes to LazzyORM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-13

### Added
- LazyUpdate class for safe UPDATE operations with parameterized queries
- LazyDelete class for safe DELETE operations with confirmation for bulk deletes
- Custom exception classes (ConnectionError, QueryError, ValidationError, etc.)
- Comprehensive input validation throughout all classes
- SQL injection protection via parameterized queries
- Context manager support for all database operation classes
- LazyQuery enhancements:
  - ORDER BY clause support
  - LIMIT and OFFSET support
  - IN and NOT IN operator support
  - first() method to get single result
  - count() method to count results
- LazyFetch enhancements:
  - Cache management with clear_cache() method
  - Support for disabling cache
  - Parameterized query support
- Comprehensive test suite with pytest
- Type hints throughout the codebase
- pyproject.toml for modern Python packaging
- CONTRIBUTING.md with development guidelines
- Improved logging with detailed error messages

### Changed
- LazyQuery now uses parameterized queries to prevent SQL injection
- Connection management improved with proper cleanup
- All database operation classes now properly close connections
- Updated README with comprehensive examples and security information
- Improved error messages for better debugging
- Logger now includes module, function, and line number information

### Fixed
- Connection leaks in LazyFetch, LazyQuery, and LazyInsert
- SQL injection vulnerability in LazyQuery.where() method
- Resource cleanup issues with cursors and connections
- Missing error handling in database operations
- Input validation gaps in column names and operators
- Connection pool exhaustion issues

### Security
- Implemented parameterized queries across all database operations
- Added input validation to prevent SQL injection
- Sanitized table and column names
- Added validation for operators and identifiers

## [0.2.4] - 2023-XX-XX

### Added
- Basic LazyFetch functionality for fetching data
- LazyInsert for inserting data from CSV files
- LazyInsert for inserting data objects
- LazyQuery for query building
- Connection pooling support
- Logger with colored console output
- Date parser utility

### Changed
- Improved connection pooling

### Fixed
- Various bug fixes

## [0.2.2] - 2023-XX-XX

### Added
- Initial public release
- Basic ORM functionality
- MySQL connection support
- Lazy loading capabilities

[0.3.0]: https://github.com/Dipendra-creator/LazzyORM/releases/tag/v0.3.0
[0.2.4]: https://github.com/Dipendra-creator/LazzyORM/releases/tag/v0.2.4
[0.2.2]: https://github.com/Dipendra-creator/LazzyORM/releases/tag/v0.2.2
