# Rulang

A lightweight DSL for business rules in Python, built with ANTLR4.

## Features

- **Expressive DSL**: Define business rules with a clean, readable syntax
- **Flexible Entity Support**: Works with dictionaries, dataclasses, and any Python object
- **Dependency Analysis**: Automatic read/write tracking and execution ordering
- **Cycle Detection**: Warns about circular dependencies and handles them gracefully
- **Workflow Integration**: Call custom Python functions from rules with dependency declarations
- **Multiple Evaluation Modes**: First-match or all-match execution
- **String Operations**: Contains, startswith, endswith, regex matching
- **Null-Safe Access**: Optional chaining (`?.`) and null coalescing (`??`)
- **Built-in Functions**: String manipulation, type coercion, collection utilities

## Installation

```bash
uv add rulang
```

## Quick Start

```python
from rulang import RuleEngine

# Create an engine
engine = RuleEngine(mode="all_match")

# Add business rules
engine.add_rules([
    "entity.age >= 18 => entity.is_adult = true",
    "entity.is_adult == true => entity.discount += 0.1",
])

# Evaluate against an entity
entity = {"age": 25, "is_adult": False, "discount": 0.0}
engine.evaluate(entity)

print(entity)  # {'age': 25, 'is_adult': True, 'discount': 0.1}
```

## DSL Syntax

### Basic Rule Structure

```
condition => action [; action]* [; ret expression]?
```

### Conditions (Left Side)

#### Comparison Operators

```python
# Basic comparisons
entity.value == 10
entity.value != 10
entity.value < 10
entity.value > 10
entity.value <= 10
entity.value >= 10

# Logical operators
entity.a > 0 and entity.b < 10
entity.a > 0 or entity.b < 10
not entity.disabled

# Membership
entity.status in ['active', 'pending']
entity.status not in ['deleted']

# Arithmetic
entity.price * entity.quantity >= 100
```

#### String Operators

```python
# Substring check
entity.subject contains "invoice"
entity.subject not contains "spam"

# Prefix/suffix matching
entity.email startswith "admin@"
entity.filename endswith ".pdf"

# Alternative syntax
entity.email starts_with "admin@"
entity.filename ends_with ".pdf"

# Regex matching
entity.code matches "INV-\\d{4}"
entity.email matches "^[a-z]+@[a-z]+\\.[a-z]+$"
```

#### Existence Operators

```python
# Check if value is not None
entity.customer_id exists

# Check if value is None, empty string, or empty collection
entity.notes is_empty

# Negated forms
not entity.email exists      # same as checking for None
not entity.items is_empty    # has content
```

#### List Operators

```python
# Check if collection contains ANY of the values
entity.recipients contains_any ["admin@co.com", "support@co.com"]

# Check if collection contains ALL of the values
entity.tags contains_all ["reviewed", "approved"]
```

#### Path Access

```python
# Nested paths
entity.user.profile.age >= 18

# List indexing (including negative indices)
entity.items[0].value > 10
entity.items[-1].total >= 100

# Null-safe access (returns None instead of error if parent is None)
entity.user?.profile?.name == "John"

# Null coalescing (provide default for None values)
entity.nickname ?? "Anonymous"
entity.config?.timeout ?? 30

# Combined null-safe access with coalescing
entity.user?.name ?? "Unknown"
```

### Built-in Functions

#### String Functions

```python
# Case conversion
lower(entity.name) == "john"
upper(entity.code) == "ABC"

# Whitespace removal
trim(entity.input) != ""
strip(entity.text) == "hello"  # alias for trim
```

#### Collection Functions

```python
# Length
len(entity.items) > 0
len(entity.name) >= 3

# First/last element
first(entity.items) == "apple"
last(entity.items) == "banana"

# Dictionary operations
"name" in keys(entity.data)
"John" in values(entity.data)
```

#### Type Coercion

```python
# Convert to integer
int(entity.quantity) > 100
int(entity.price) == 99  # truncates decimals

# Convert to float
float(entity.amount) >= 99.99

# Convert to string
str(entity.code) == "123"

# Convert to boolean
bool(entity.value) == true
```

#### Math Functions

```python
# Absolute value
abs(entity.difference) < 10

# Rounding
round(entity.price, 2) == 99.99
round(entity.total) == 100  # rounds to integer

# Min/max
min(entity.a, entity.b, entity.c) > 0
max(entity.x, entity.y) < 100
```

#### Type Checking

```python
# Check types
is_list(entity.items) == true
is_string(entity.name) == true
is_number(entity.count) == true
is_none(entity.value) == true
```

### List Any-Satisfies Semantics

When comparing a list field with a scalar value using `==`, `!=`, `in`, `contains`, `startswith`, `endswith`, or `matches`, the comparison returns true if ANY element in the list satisfies the condition:

```python
# If entity.tags = ["urgent", "finance"]
entity.tags == "urgent"           # True (any element matches)
entity.tags contains "urg"        # True (any element contains substring)
entity.tags startswith "fin"      # True (any element starts with prefix)

# If entity.domains = ["admin.example.com", "user.example.com"]
entity.domains startswith "admin" # True (first domain matches)
entity.domains endswith ".com"    # True (all domains match, but only one needed)
```

When comparing two lists, exact equality is used:

```python
entity.tags == ["a", "b", "c"]    # True only if tags is exactly ["a", "b", "c"]
```

### Actions (Right Side)

```python
# Simple assignment
entity.status = 'processed'

# Compound assignments
entity.counter += 1
entity.total -= 10
entity.price *= 0.9
entity.value /= 2

# Workflow calls
workflow('process_order')
workflow('send_notification', entity.user_id)

# Return values
ret true
ret entity
ret entity.total * 1.2

# Multiple actions
entity.processed = true; workflow('notify'); ret entity
```

## Workflows

Workflows allow you to call Python functions from rules:

```python
from rulang import RuleEngine, Workflow

# Using the decorator
@RuleEngine.workflow("calculate_tax", reads=["entity.subtotal"], writes=["entity.tax"])
def calculate_tax(entity):
    entity["tax"] = entity["subtotal"] * 0.2

# Using the Workflow wrapper
def apply_discount(entity):
    entity["total"] = entity["subtotal"] * 0.9

workflows = {
    "apply_discount": Workflow(
        fn=apply_discount,
        reads=["entity.subtotal"],
        writes=["entity.total"]
    )
}

engine = RuleEngine()
engine.add_rules("entity.eligible == true => workflow('apply_discount')")
engine.evaluate(entity, workflows=workflows)
```

The `reads` and `writes` declarations enable accurate dependency analysis even though the rule engine can't inspect the workflow's internal logic.

## Evaluation Modes

### First Match (default)

Stops after the first matching rule:

```python
engine = RuleEngine(mode="first_match")
engine.add_rules([
    "entity.value > 100 => ret 'high'",
    "entity.value > 50 => ret 'medium'",
    "entity.value > 0 => ret 'low'",
])

result = engine.evaluate({"value": 75})  # Returns 'medium'
```

### All Match

Executes all matching rules in dependency order:

```python
engine = RuleEngine(mode="all_match")
engine.add_rules([
    "entity.age >= 18 => entity.is_adult = true",
    "entity.is_adult == true => entity.can_vote = true",
])

entity = {"age": 25, "is_adult": False, "can_vote": False}
engine.evaluate(entity)
# Both rules execute in correct order
```

## Dependency Graph

The engine automatically analyzes read/write patterns to determine execution order:

```python
engine = RuleEngine(mode="all_match")
engine.add_rules([
    "entity.b > 0 => entity.c = 1",  # Rule 0: reads b, writes c
    "entity.a > 0 => entity.b = 1",  # Rule 1: reads a, writes b
])

# Rule 1 executes before Rule 0 (Rule 0 depends on Rule 1's output)
print(engine.get_execution_order())  # [1, 0]

# Inspect the dependency graph
print(engine.get_dependency_graph())  # {1: {0}}  # Rule 0 depends on Rule 1
```

## Real-World Examples

### Email Classification

```python
engine = RuleEngine(mode="first_match")
engine.add_rules([
    # High priority: urgent emails from known domains
    "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",

    # Invoice detection
    "entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",

    # Spam detection
    "entity.from_domain not in ['company.com'] and lower(entity.subject) contains 'winner' => ret 'spam'",

    # Default
    "true => ret 'normal'"
])
```

### Order Processing

```python
engine = RuleEngine(mode="all_match")
engine.add_rules([
    # Apply member discount
    "entity.customer?.membership exists and entity.customer.membership != 'none' => entity.discount = 0.1",

    # Free shipping for large orders
    "entity.subtotal >= 100 => entity.shipping = 0",

    # Calculate total
    "true => entity.total = (entity.subtotal * (1 - (entity.discount ?? 0))) + (entity.shipping ?? 5.99)",

    # Flag for review if total is high
    "entity.total > 1000 => entity.needs_review = true"
])
```

### Data Validation

```python
engine = RuleEngine(mode="all_match")
engine.add_rules([
    # Required fields
    "entity.email is_empty => entity.errors += ['Email is required']",
    "entity.name is_empty => entity.errors += ['Name is required']",

    # Format validation
    "not entity.email is_empty and not entity.email matches '^[^@]+@[^@]+\\.[^@]+$' => entity.errors += ['Invalid email format']",

    # Length validation
    "len(entity.name ?? '') > 100 => entity.errors += ['Name too long']",

    # Set validity flag
    "len(entity.errors) == 0 => entity.is_valid = true"
])

entity = {"email": "", "name": "John", "errors": [], "is_valid": False}
engine.evaluate(entity)
print(entity["errors"])  # ['Email is required']
```

## Error Handling

```python
from rulang import (
    RuleEngine,
    RuleSyntaxError,
    PathResolutionError,
    WorkflowNotFoundError,
)

engine = RuleEngine()

# Syntax errors
try:
    engine.add_rules("invalid syntax")
except RuleSyntaxError as e:
    print(f"Parse error: {e}")

# Missing attributes
try:
    engine.add_rules("entity.missing.path > 0 => ret true")
    engine.evaluate({"name": "test"})
except PathResolutionError as e:
    print(f"Path error: {e}")

# Missing workflows
try:
    engine.add_rules("entity.x > 0 => workflow('unknown')")
    engine.evaluate({"x": 1})
except WorkflowNotFoundError as e:
    print(f"Workflow error: {e}")
```

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# Regenerate parser (after grammar changes)
uv run antlr4 -Dlanguage=Python3 -visitor -o src/rule_interpreter/grammar/generated src/rule_interpreter/grammar/BusinessRules.g4
```

## License

MIT
