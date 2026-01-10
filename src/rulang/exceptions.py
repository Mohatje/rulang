"""
Custom exceptions for Rulang.
"""


class RuleInterpreterError(Exception):
    """Base exception for all Rulang errors."""

    pass


class PathResolutionError(RuleInterpreterError):
    """Raised when an attribute path cannot be resolved on an entity."""

    def __init__(self, path: str, entity_type: str, reason: str = ""):
        self.path = path
        self.entity_type = entity_type
        self.reason = reason
        message = f"Cannot resolve path '{path}' on entity of type '{entity_type}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class RuleSyntaxError(RuleInterpreterError):
    """Raised when a rule string cannot be parsed."""

    def __init__(self, rule: str, message: str, line: int | None = None, column: int | None = None):
        self.rule = rule
        self.line = line
        self.column = column
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        super().__init__(f"Syntax error{location}: {message}\nRule: {rule}")


class CyclicDependencyWarning(UserWarning):
    """Warning issued when a cyclic dependency is detected in rules."""

    def __init__(self, cycle: list[int]):
        self.cycle = cycle
        cycle_str = " -> ".join(str(i) for i in cycle)
        super().__init__(f"Cyclic dependency detected in rules: {cycle_str}")


class WorkflowNotFoundError(RuleInterpreterError):
    """Raised when a workflow function is not found."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Workflow '{name}' not found in registered workflows")


class EvaluationError(RuleInterpreterError):
    """Raised when an error occurs during rule evaluation."""

    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(f"Error evaluating rule: {message}\nRule: {rule}")

