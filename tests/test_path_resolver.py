"""Comprehensive tests for path resolver."""

import pytest
from dataclasses import dataclass, field
from typing import Any

from rulang.path_resolver import PathResolver
from rulang.exceptions import PathResolutionError


class TestDictEntityResolution:
    """Test path resolution on dictionary entities."""

    def test_simple_path(self):
        entity = {"name": "test"}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "name"]) == "test"

    def test_nested_path(self):
        entity = {"user": {"profile": {"name": "John"}}}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "user", "profile", "name"]) == "John"

    def test_deep_nesting(self):
        entity = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {"j": "deep"}}}}}}}}}}
        resolver = PathResolver(entity)
        path = ["entity"] + [chr(ord("a") + i) for i in range(10)]
        assert resolver.resolve(path) == "deep"

    def test_list_index_positive(self):
        entity = {"items": [{"value": 10}, {"value": 20}, {"value": 30}]}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "items", 0, "value"]) == 10
        assert resolver.resolve(["entity", "items", 1, "value"]) == 20
        assert resolver.resolve(["entity", "items", 2, "value"]) == 30

    def test_list_index_negative(self):
        entity = {"items": [{"value": 10}, {"value": 20}, {"value": 30}]}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "items", -1, "value"]) == 30
        assert resolver.resolve(["entity", "items", -2, "value"]) == 20
        assert resolver.resolve(["entity", "items", -3, "value"]) == 10

    def test_list_index_zero(self):
        entity = {"items": [{"value": 10}]}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "items", 0, "value"]) == 10

    def test_list_index_out_of_bounds_positive(self):
        entity = {"items": [{"value": 10}]}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "items", 10, "value"])

    def test_list_index_out_of_bounds_negative(self):
        entity = {"items": [{"value": 10}]}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "items", -10, "value"])

    def test_mixed_dict_list_path(self):
        entity = {
            "users": [
                {"name": "Alice", "scores": [10, 20, 30]},
                {"name": "Bob", "scores": [15, 25, 35]},
            ]
        }
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "users", 0, "name"]) == "Alice"
        assert resolver.resolve(["entity", "users", 0, "scores", 1]) == 20
        assert resolver.resolve(["entity", "users", -1, "scores", -1]) == 35

    def test_empty_dict(self):
        entity = {}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "missing"])

    def test_dict_with_none_values(self):
        entity = {"value": None, "nested": {"value": None}}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "value"]) is None
        assert resolver.resolve(["entity", "nested", "value"]) is None

    def test_dict_with_empty_string_keys(self):
        entity = {"": "empty_key", "normal": "normal_key"}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", ""]) == "empty_key"

    def test_dict_with_numeric_keys(self):
        entity = {1: "numeric", "string": "string_key"}
        resolver = PathResolver(entity)
        # Note: numeric keys accessed as strings in path
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "1"])

    def test_very_long_path(self):
        entity = {}
        current = entity
        for i in range(20):
            current[f"level{i}"] = {}
            current = current[f"level{i}"]
        current["value"] = "deep"

        resolver = PathResolver(entity)
        path = ["entity"] + [f"level{i}" for i in range(20)] + ["value"]
        assert resolver.resolve(path) == "deep"


class TestDictEntityAssignment:
    """Test assignment operations on dictionary entities."""

    def test_simple_assignment(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 20)
        assert entity["value"] == 20

    def test_assignment_create_new_key(self):
        entity = {}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "new_key"], "new_value")
        assert entity["new_key"] == "new_value"

    def test_nested_assignment(self):
        entity = {"user": {"profile": {}}}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "user", "profile", "name"], "John")
        assert entity["user"]["profile"]["name"] == "John"

    def test_list_index_assignment(self):
        entity = {"items": [{"value": 10}, {"value": 20}]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 0, "value"], 100)
        assert entity["items"][0]["value"] == 100

    def test_assignment_to_nonexistent_parent(self):
        entity = {}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.assign(["entity", "missing", "nested"], "value")

    def test_compound_assignment_simulation(self):
        entity = {"counter": 10}
        resolver = PathResolver(entity)
        current = resolver.resolve(["entity", "counter"])
        resolver.assign(["entity", "counter"], current + 5)
        assert entity["counter"] == 15


class TestObjectEntityResolution:
    """Test path resolution on object entities."""

    def test_simple_attribute(self):
        @dataclass
        class Entity:
            name: str

        entity = Entity(name="test")
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "name"]) == "test"

    def test_nested_attributes(self):
        @dataclass
        class Profile:
            name: str

        @dataclass
        class User:
            profile: Profile

        @dataclass
        class Entity:
            user: User

        entity = Entity(user=User(profile=Profile(name="John")))
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "user", "profile", "name"]) == "John"

    def test_dataclass_with_defaults(self):
        @dataclass
        class Entity:
            name: str = "default"
            value: int = 0

        entity = Entity()
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "name"]) == "default"
        assert resolver.resolve(["entity", "value"]) == 0

    def test_missing_attribute(self):
        @dataclass
        class Entity:
            name: str

        entity = Entity(name="test")
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "missing"])

    def test_property_access(self):
        class Entity:
            def __init__(self):
                self._value = 10

            @property
            def value(self):
                return self._value

        entity = Entity()
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "value"]) == 10

    def test_custom_getattr(self):
        class Entity:
            def __init__(self):
                self.data = {"a": 1, "b": 2}

            def __getattr__(self, name):
                return self.data.get(name)

        entity = Entity()
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "a"]) == 1
        assert resolver.resolve(["entity", "b"]) == 2


class TestObjectEntityAssignment:
    """Test assignment operations on object entities."""

    def test_simple_assignment(self):
        @dataclass
        class Entity:
            value: int

        entity = Entity(value=10)
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 20)
        assert entity.value == 20

    def test_nested_assignment(self):
        @dataclass
        class Nested:
            value: int

        @dataclass
        class Entity:
            nested: Nested

        entity = Entity(nested=Nested(value=10))
        resolver = PathResolver(entity)
        resolver.assign(["entity", "nested", "value"], 20)
        assert entity.nested.value == 20

    def test_frozen_dataclass_error(self):
        @dataclass(frozen=True)
        class Entity:
            value: int

        entity = Entity(value=10)
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.assign(["entity", "value"], 20)

    def test_property_without_setter_error(self):
        class Entity:
            def __init__(self):
                self._value = 10

            @property
            def value(self):
                return self._value

        entity = Entity()
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.assign(["entity", "value"], 20)


class TestListEntityResolution:
    """Test path resolution on list/sequence entities."""

    def test_list_access(self):
        entity = [10, 20, 30]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        assert resolver.resolve(["list", 0]) == 10
        assert resolver.resolve(["list", 1]) == 20
        assert resolver.resolve(["list", 2]) == 30

    def test_list_negative_index(self):
        entity = [10, 20, 30]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        assert resolver.resolve(["list", -1]) == 30
        assert resolver.resolve(["list", -2]) == 20
        assert resolver.resolve(["list", -3]) == 10

    def test_list_out_of_bounds(self):
        entity = [10]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["list", 10])

    def test_list_assignment(self):
        entity = [10, 20, 30]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        resolver.assign(["list", 1], 100)
        assert entity[1] == 100

    def test_empty_list(self):
        entity = []
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["list", 0])

    def test_list_with_none_elements(self):
        entity = [None, 10, None]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        assert resolver.resolve(["list", 0]) is None
        assert resolver.resolve(["list", 1]) == 10


class TestMixedEntityTypes:
    """Test path resolution with mixed entity types."""

    def test_dict_object_mixed(self):
        @dataclass
        class User:
            name: str

        entity = {"user": User(name="John")}
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "user", "name"]) == "John"

    def test_object_dict_mixed(self):
        @dataclass
        class Entity:
            data: dict

        entity = Entity(data={"value": 10})
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "data", "value"]) == 10

    def test_list_dict_mixed(self):
        entity = [{"value": 10}, {"value": 20}]
        resolver = PathResolver(entity, entity_name="list")
        resolver.add_to_context("list", entity)
        assert resolver.resolve(["list", 0, "value"]) == 10

    def test_complex_nested_structure(self):
        @dataclass
        class Profile:
            scores: list

        @dataclass
        class User:
            profile: Profile

        entity = {
            "users": [
                User(profile=Profile(scores=[10, 20])),
                User(profile=Profile(scores=[30, 40])),
            ]
        }
        resolver = PathResolver(entity)
        assert resolver.resolve(["entity", "users", 0, "profile", "scores", 1]) == 20


class TestPathResolverEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_path(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve([])

    def test_path_must_start_with_identifier(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve([0, "value"])

    def test_unknown_root_identifier(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve(["unknown", "value"])

    def test_non_integer_index(self):
        entity = {"items": [10, 20]}
        resolver = PathResolver(entity)
        # Non-integer indices should be treated as string keys
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "items", "0"])

    def test_resolve_for_assignment_minimum_path(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        with pytest.raises(PathResolutionError):
            resolver.resolve_for_assignment(["entity"])

    def test_context_management(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.add_to_context("other", {"data": 20})
        assert resolver.resolve(["other", "data"]) == 20

