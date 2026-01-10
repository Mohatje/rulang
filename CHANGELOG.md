# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-10

### Added

- Core rule engine with DSL for business rules evaluation
- ANTLR4-based parser for rule syntax
- Dependency graph analysis with cycle detection
- Path resolution for nested entity access with null-safe operators (`?.`, `?[]`)
- Workflow support with decorator-based registration
- Comprehensive operators:
  - Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
  - Logical: `AND`, `OR`, `NOT`
  - String: `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `MATCHES`
  - Existence: `EXISTS`, `NOT EXISTS`, `IS NULL`, `IS NOT NULL`, `IS EMPTY`, `IS NOT EMPTY`
  - List: `IN`, `NOT IN`, `ALL IN`, `ANY IN`, `NONE IN`
- Built-in functions for strings, collections, type coercion, and math
- Custom exception hierarchy for error handling
