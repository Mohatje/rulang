# Shared Spec

The files in `spec/cases` describe language-neutral behavior that both the
Python and TypeScript runtimes must satisfy.

These cases intentionally cover the portable DSL semantics:

- parsing and syntax errors
- entity mutation and return values
- dependency analysis and execution order
- null-safe access and null coalescing
- built-in functions and operator semantics

Language-specific behaviors should stay in runtime-local test suites.
