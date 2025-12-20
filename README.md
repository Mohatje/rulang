# Rule Interpreter

A lightweight DSL for business rules in Python, built with ANTLR4.

## Features

- **Expressive DSL**: Define business rules with a clean, readable syntax
- **Flexible Entity Support**: Works with dictionaries, dataclasses, and any Python object
- **Dependency Analysis**: Automatic read/write tracking and execution ordering
- **Cycle Detection**: Warns about circular dependencies and handles them gracefully
- **Workflow Integration**: Call custom Python functions from rules with dependency declarations
- **Multiple Evaluation Modes**: First-match or all-match execution

## Installation

```bash
uv add rule-interpreter
```

## Quick Start

```python
from rule_interpreter import RuleEngine

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

```python
# Comparisons
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

# Nested paths
entity.user.profile.age >= 18

# List indexing
entity.items[0].value > 10
entity.items[-1].total >= 100
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
from rule_interpreter import RuleEngine, Workflow

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

## Error Handling

```python
from rule_interpreter import (
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

