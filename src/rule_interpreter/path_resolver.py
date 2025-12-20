"""
Path resolver for flexible entity attribute access.

Supports:
- Dictionaries (nested dict access)
- Objects (using getattr)
- Dataclasses / Pydantic models
- List indexing (including negative indices)
"""

from dataclasses import fields, is_dataclass
from typing import Any

from rule_interpreter.exceptions import PathResolutionError


def _is_dict_like(obj: Any) -> bool:
    """Check if object supports dict-like access."""
    return isinstance(obj, dict) or hasattr(obj, "__getitem__") and hasattr(obj, "keys")


def _get_attribute(obj: Any, key: str) -> Any:
    """Get an attribute from an object, supporting dicts and objects."""
    # Try dict-like access first for dicts
    if isinstance(obj, dict):
        if key not in obj:
            raise KeyError(key)
        return obj[key]

    # Try attribute access for objects
    if hasattr(obj, key):
        return getattr(obj, key)

    # Try dict-like access for other mappings
    if hasattr(obj, "__getitem__") and hasattr(obj, "keys"):
        try:
            return obj[key]
        except (KeyError, TypeError):
            pass

    raise AttributeError(f"'{type(obj).__name__}' has no attribute '{key}'")


def _get_index(obj: Any, index: int) -> Any:
    """Get an item by index from a sequence."""
    if not hasattr(obj, "__getitem__"):
        raise TypeError(f"'{type(obj).__name__}' does not support indexing")
    return obj[index]


def _set_attribute(obj: Any, key: str, value: Any) -> None:
    """Set an attribute on an object, supporting dicts and objects."""
    if isinstance(obj, dict):
        obj[key] = value
    elif hasattr(obj, "__setitem__") and hasattr(obj, "keys"):
        obj[key] = value
    else:
        setattr(obj, key, value)


def _set_index(obj: Any, index: int, value: Any) -> None:
    """Set an item by index in a sequence."""
    if not hasattr(obj, "__setitem__"):
        raise TypeError(f"'{type(obj).__name__}' does not support index assignment")
    obj[index] = value


class PathResolver:
    """
    Resolves attribute paths on entities.

    Paths can include:
    - Dot notation: entity.user.name
    - Bracket notation for indices: entity.items[0]
    - Negative indices: entity.items[-1]
    """

    def __init__(self, entity: Any, entity_name: str = "entity"):
        """
        Initialize the path resolver.

        Args:
            entity: The root entity to resolve paths on
            entity_name: The name used in path expressions (default: "entity")
        """
        self.entity = entity
        self.entity_name = entity_name
        self._context: dict[str, Any] = {entity_name: entity}

    def add_to_context(self, name: str, value: Any) -> None:
        """Add a variable to the resolution context."""
        self._context[name] = value

    def resolve(self, path_parts: list[str | int]) -> Any:
        """
        Resolve a path to get its value.

        Args:
            path_parts: List of path components (strings for attributes, ints for indices)

        Returns:
            The resolved value

        Raises:
            PathResolutionError: If the path cannot be resolved
        """
        if not path_parts:
            raise PathResolutionError("", type(self.entity).__name__, "Empty path")

        # Get the root from context
        root_name = path_parts[0]
        if not isinstance(root_name, str):
            raise PathResolutionError(
                str(path_parts), type(self.entity).__name__, f"Path must start with an identifier, got {type(root_name)}"
            )

        if root_name not in self._context:
            raise PathResolutionError(str(path_parts), type(self.entity).__name__, f"Unknown identifier '{root_name}'")

        current = self._context[root_name]
        path_str = root_name

        for part in path_parts[1:]:
            try:
                if isinstance(part, int):
                    path_str += f"[{part}]"
                    current = _get_index(current, part)
                else:
                    path_str += f".{part}"
                    current = _get_attribute(current, part)
            except (KeyError, AttributeError, IndexError, TypeError) as e:
                raise PathResolutionError(path_str, type(self.entity).__name__, str(e)) from e

        return current

    def resolve_for_assignment(self, path_parts: list[str | int]) -> tuple[Any, str | int]:
        """
        Resolve a path for assignment, returning the parent object and the final key/index.

        Args:
            path_parts: List of path components

        Returns:
            Tuple of (parent_object, final_key_or_index)

        Raises:
            PathResolutionError: If the path cannot be resolved
        """
        if len(path_parts) < 2:
            raise PathResolutionError(str(path_parts), type(self.entity).__name__, "Cannot assign to root object")

        # Resolve all but the last part
        parent = self.resolve(path_parts[:-1])
        return parent, path_parts[-1]

    def assign(self, path_parts: list[str | int], value: Any) -> None:
        """
        Assign a value to a path.

        Args:
            path_parts: List of path components
            value: The value to assign

        Raises:
            PathResolutionError: If the path cannot be resolved for assignment
        """
        parent, key = self.resolve_for_assignment(path_parts)

        try:
            if isinstance(key, int):
                _set_index(parent, key, value)
            else:
                _set_attribute(parent, key, value)
        except (TypeError, AttributeError) as e:
            path_str = self._path_to_string(path_parts)
            raise PathResolutionError(path_str, type(self.entity).__name__, str(e)) from e

    def _path_to_string(self, path_parts: list[str | int]) -> str:
        """Convert path parts to a string representation."""
        if not path_parts:
            return ""
        result = str(path_parts[0])
        for part in path_parts[1:]:
            if isinstance(part, int):
                result += f"[{part}]"
            else:
                result += f".{part}"
        return result

