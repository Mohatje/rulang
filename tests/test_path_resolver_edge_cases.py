"""Edge case tests for PathResolver."""

import pytest
from dataclasses import dataclass
from rule_interpreter.path_resolver import PathResolver
from rule_interpreter.exceptions import PathResolutionError


class TestPathResolverEdgeCases:
    """Test edge cases in PathResolver."""

    def test_resolve_empty_path(self):
        """Test resolving empty path raises error."""
        resolver = PathResolver({"value": 10})
        with pytest.raises(PathResolutionError):
            resolver.resolve([])

    def test_resolve_nonexistent_root(self):
        """Test resolving path with nonexistent root."""
        resolver = PathResolver({"value": 10})
        with pytest.raises(PathResolutionError):
            resolver.resolve(["nonexistent", "path"])

    def test_resolve_with_custom_entity_name(self):
        """Test resolving with custom entity name."""
        resolver = PathResolver({"value": 10}, entity_name="custom")
        result = resolver.resolve(["custom", "value"])
        assert result == 10

    def test_resolve_nonexistent_root_custom_name(self):
        """Test resolving with wrong root name."""
        resolver = PathResolver({"value": 10}, entity_name="custom")
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "value"])

    def test_assign_empty_path(self):
        """Test assigning to empty path raises error."""
        resolver = PathResolver({"value": 10})
        with pytest.raises(PathResolutionError):
            resolver.assign([], 20)

    def test_assign_nonexistent_root(self):
        """Test assigning to nonexistent root."""
        resolver = PathResolver({"value": 10})
        with pytest.raises(PathResolutionError):
            resolver.assign(["nonexistent", "path"], 20)

    def test_resolve_dict_with_none_value(self):
        """Test resolving dict with None value."""
        resolver = PathResolver({"value": None})
        result = resolver.resolve(["entity", "value"])
        assert result is None

    def test_resolve_dict_with_false_value(self):
        """Test resolving dict with False value."""
        resolver = PathResolver({"value": False})
        result = resolver.resolve(["entity", "value"])
        assert result is False

    def test_resolve_dict_with_zero_value(self):
        """Test resolving dict with zero value."""
        resolver = PathResolver({"value": 0})
        result = resolver.resolve(["entity", "value"])
        assert result == 0

    def test_resolve_dict_with_empty_string(self):
        """Test resolving dict with empty string."""
        resolver = PathResolver({"value": ""})
        result = resolver.resolve(["entity", "value"])
        assert result == ""

    def test_resolve_dict_with_empty_list(self):
        """Test resolving dict with empty list."""
        resolver = PathResolver({"value": []})
        result = resolver.resolve(["entity", "value"])
        assert result == []

    def test_resolve_dict_with_empty_dict(self):
        """Test resolving dict with empty dict."""
        resolver = PathResolver({"value": {}})
        result = resolver.resolve(["entity", "value"])
        assert result == {}

    def test_resolve_nested_dict_deep(self):
        """Test resolving deeply nested dict."""
        resolver = PathResolver({"a": {"b": {"c": {"d": {"e": 10}}}}})
        result = resolver.resolve(["entity", "a", "b", "c", "d", "e"])
        assert result == 10

    def test_resolve_list_with_none_element(self):
        """Test resolving list with None element."""
        resolver = PathResolver({"items": [None, 1, 2]})
        result = resolver.resolve(["entity", "items", 0])
        assert result is None

    def test_resolve_list_with_false_element(self):
        """Test resolving list with False element."""
        resolver = PathResolver({"items": [False, True]})
        result = resolver.resolve(["entity", "items", 0])
        assert result is False

    def test_resolve_list_with_zero_element(self):
        """Test resolving list with zero element."""
        resolver = PathResolver({"items": [0, 1, 2]})
        result = resolver.resolve(["entity", "items", 0])
        assert result == 0

    def test_resolve_list_with_empty_string_element(self):
        """Test resolving list with empty string element."""
        resolver = PathResolver({"items": ["", "a", "b"]})
        result = resolver.resolve(["entity", "items", 0])
        assert result == ""

    def test_resolve_list_with_negative_index_zero(self):
        """Test resolving list with negative index -0."""
        resolver = PathResolver({"items": [10, 20, 30]})
        # -0 is same as 0
        result = resolver.resolve(["entity", "items", -0])
        assert result == 10

    def test_resolve_list_with_large_negative_index(self):
        """Test resolving list with large negative index."""
        resolver = PathResolver({"items": [10, 20, 30]})
        result = resolver.resolve(["entity", "items", -3])
        assert result == 10

    def test_resolve_list_with_very_large_index(self):
        """Test resolving list with very large index."""
        resolver = PathResolver({"items": [10, 20, 30]})
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "items", 999999])

    def test_resolve_list_with_very_large_negative_index(self):
        """Test resolving list with very large negative index."""
        resolver = PathResolver({"items": [10, 20, 30]})
        with pytest.raises(PathResolutionError):
            resolver.resolve(["entity", "items", -999999])

    def test_resolve_mixed_dict_list_path(self):
        """Test resolving path mixing dict and list."""
        resolver = PathResolver({"data": {"items": [{"value": 10}]}})
        result = resolver.resolve(["entity", "data", "items", 0, "value"])
        assert result == 10

    def test_resolve_object_with_none_attribute(self):
        """Test resolving object with None attribute."""
        class Entity:
            def __init__(self):
                self.value = None
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result is None

    def test_resolve_object_with_false_attribute(self):
        """Test resolving object with False attribute."""
        class Entity:
            def __init__(self):
                self.value = False
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result is False

    def test_resolve_object_with_zero_attribute(self):
        """Test resolving object with zero attribute."""
        class Entity:
            def __init__(self):
                self.value = 0
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result == 0

    def test_resolve_object_with_empty_string_attribute(self):
        """Test resolving object with empty string attribute."""
        class Entity:
            def __init__(self):
                self.value = ""
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result == ""

    def test_resolve_object_with_property(self):
        """Test resolving object with property."""
        class Entity:
            def __init__(self):
                self._value = 10
            
            @property
            def value(self):
                return self._value
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result == 10

    def test_resolve_object_with_method(self):
        """Test resolving object with method (returns method object)."""
        class Entity:
            def method(self):
                return 10
        
        resolver = PathResolver(Entity())
        # Methods can be resolved as attributes in Python
        result = resolver.resolve(["entity", "method"])
        assert callable(result)

    def test_resolve_dataclass_with_default(self):
        """Test resolving dataclass with default value."""
        @dataclass
        class Entity:
            value: int = 0
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "value"])
        assert result == 0

    def test_assign_dict_with_none(self):
        """Test assigning None to dict."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], None)
        assert entity["value"] is None

    def test_assign_dict_with_false(self):
        """Test assigning False to dict."""
        entity = {"value": True}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], False)
        assert entity["value"] is False

    def test_assign_dict_with_zero(self):
        """Test assigning zero to dict."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 0)
        assert entity["value"] == 0

    def test_assign_dict_with_empty_string(self):
        """Test assigning empty string to dict."""
        entity = {"value": "test"}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], "")
        assert entity["value"] == ""

    def test_assign_dict_with_empty_list(self):
        """Test assigning empty list to dict."""
        entity = {"value": [1, 2, 3]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], [])
        assert entity["value"] == []

    def test_assign_dict_with_empty_dict(self):
        """Test assigning empty dict to dict."""
        entity = {"value": {"a": 1}}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], {})
        assert entity["value"] == {}

    def test_assign_list_with_none(self):
        """Test assigning None to list element."""
        entity = {"items": [10, 20, 30]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 0], None)
        assert entity["items"][0] is None

    def test_assign_list_with_false(self):
        """Test assigning False to list element."""
        entity = {"items": [True, True]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 0], False)
        assert entity["items"][0] is False

    def test_assign_list_with_zero(self):
        """Test assigning zero to list element."""
        entity = {"items": [10, 20]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 0], 0)
        assert entity["items"][0] == 0

    def test_assign_list_with_negative_index(self):
        """Test assigning to list with negative index."""
        entity = {"items": [10, 20, 30]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", -1], 100)
        assert entity["items"][-1] == 100

    def test_assign_object_with_none(self):
        """Test assigning None to object attribute."""
        class Entity:
            def __init__(self):
                self.value = 10
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], None)
        assert entity.value is None

    def test_assign_object_with_false(self):
        """Test assigning False to object attribute."""
        class Entity:
            def __init__(self):
                self.value = True
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], False)
        assert entity.value is False

    def test_assign_object_with_zero(self):
        """Test assigning zero to object attribute."""
        class Entity:
            def __init__(self):
                self.value = 10
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 0)
        assert entity.value == 0

    def test_assign_dataclass_with_none(self):
        """Test assigning None to dataclass field."""
        @dataclass
        class Entity:
            value: int = 10
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], None)
        assert entity.value is None

    def test_assign_dataclass_with_false(self):
        """Test assigning False to dataclass field."""
        @dataclass
        class Entity:
            value: bool = True
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], False)
        assert entity.value is False

    def test_assign_with_none_value(self):
        """Test assigning None value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], None)
        assert entity["value"] is None

    def test_assign_with_zero_value(self):
        """Test assigning zero value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 0)
        assert entity["value"] == 0

    def test_assign_with_one_value(self):
        """Test assigning one value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 1)
        assert entity["value"] == 1

    def test_assign_with_float_value(self):
        """Test assigning float value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 10.0)
        assert entity["value"] == 10.0

    def test_assign_with_negative_value(self):
        """Test assigning negative value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], -5)
        assert entity["value"] == -5

    def test_assign_with_negative_zero(self):
        """Test assigning negative zero."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], -0)
        assert entity["value"] == 0

    def test_assign_with_large_value(self):
        """Test assigning large value."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        large_val = 999999999999999999
        resolver.assign(["entity", "value"], large_val)
        assert entity["value"] == large_val

    def test_assign_with_zero_value_to_zero(self):
        """Test assigning zero to zero."""
        entity = {"value": 0}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "value"], 0)
        assert entity["value"] == 0

    def test_resolve_path_with_special_chars_in_key(self):
        """Test resolving path with special characters in key."""
        entity = {"key_with_underscore": 10, "key-with-dash": 20}
        resolver = PathResolver(entity)
        result = resolver.resolve(["entity", "key_with_underscore"])
        assert result == 10
        # Keys with dashes might not be valid identifiers
        # This depends on how the grammar handles them

    def test_assign_path_with_special_chars_in_key(self):
        """Test assigning to path with special characters in key."""
        entity = {"key_with_underscore": 10}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "key_with_underscore"], 20)
        assert entity["key_with_underscore"] == 20

    def test_resolve_nested_list_in_list(self):
        """Test resolving nested list in list."""
        resolver = PathResolver({"matrix": [[1, 2], [3, 4]]})
        result = resolver.resolve(["entity", "matrix", 0, 1])
        assert result == 2

    def test_assign_nested_list_in_list(self):
        """Test assigning to nested list in list."""
        entity = {"matrix": [[1, 2], [3, 4]]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "matrix", 0, 1], 99)
        assert entity["matrix"][0][1] == 99

    def test_resolve_dict_in_list(self):
        """Test resolving dict in list."""
        resolver = PathResolver({"items": [{"value": 10}, {"value": 20}]})
        result = resolver.resolve(["entity", "items", 1, "value"])
        assert result == 20

    def test_assign_dict_in_list(self):
        """Test assigning to dict in list."""
        entity = {"items": [{"value": 10}, {"value": 20}]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 1, "value"], 99)
        assert entity["items"][1]["value"] == 99

    def test_resolve_list_in_dict(self):
        """Test resolving list in dict."""
        resolver = PathResolver({"data": {"items": [10, 20, 30]}})
        result = resolver.resolve(["entity", "data", "items", 1])
        assert result == 20

    def test_assign_list_in_dict(self):
        """Test assigning to list in dict."""
        entity = {"data": {"items": [10, 20, 30]}}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "data", "items", 1], 99)
        assert entity["data"]["items"][1] == 99

    def test_resolve_object_in_list(self):
        """Test resolving object in list."""
        class Item:
            def __init__(self, value):
                self.value = value
        
        resolver = PathResolver({"items": [Item(10), Item(20)]})
        result = resolver.resolve(["entity", "items", 1, "value"])
        assert result == 20

    def test_assign_object_in_list(self):
        """Test assigning to object in list."""
        class Item:
            def __init__(self, value):
                self.value = value
        
        entity = {"items": [Item(10), Item(20)]}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 1, "value"], 99)
        assert entity["items"][1].value == 99

    def test_resolve_list_in_object(self):
        """Test resolving list in object."""
        class Entity:
            def __init__(self):
                self.items = [10, 20, 30]
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "items", 1])
        assert result == 20

    def test_assign_list_in_object(self):
        """Test assigning to list in object."""
        class Entity:
            def __init__(self):
                self.items = [10, 20, 30]
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "items", 1], 99)
        assert entity.items[1] == 99

    def test_resolve_dict_in_object(self):
        """Test resolving dict in object."""
        class Entity:
            def __init__(self):
                self.data = {"value": 10}
        
        resolver = PathResolver(Entity())
        result = resolver.resolve(["entity", "data", "value"])
        assert result == 10

    def test_assign_dict_in_object(self):
        """Test assigning to dict in object."""
        class Entity:
            def __init__(self):
                self.data = {"value": 10}
        
        entity = Entity()
        resolver = PathResolver(entity)
        resolver.assign(["entity", "data", "value"], 99)
        assert entity.data["value"] == 99

    def test_resolve_object_in_dict(self):
        """Test resolving object in dict."""
        class Item:
            def __init__(self, value):
                self.value = value
        
        resolver = PathResolver({"item": Item(10)})
        result = resolver.resolve(["entity", "item", "value"])
        assert result == 10

    def test_assign_object_in_dict(self):
        """Test assigning to object in dict."""
        class Item:
            def __init__(self, value):
                self.value = value

        entity = {"item": Item(10)}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "item", "value"], 99)
        assert entity["item"].value == 99


class TestDictLikeObjects:
    """Test dict-like object handling."""

    def test_is_dict_like_with_regular_dict(self):
        """Test _is_dict_like with dict."""
        from rule_interpreter.path_resolver import _is_dict_like
        assert _is_dict_like({"a": 1}) is True

    def test_is_dict_like_with_non_dict(self):
        """Test _is_dict_like with non-dict."""
        from rule_interpreter.path_resolver import _is_dict_like
        assert _is_dict_like("string") is False
        assert _is_dict_like(123) is False
        assert _is_dict_like([1, 2, 3]) is False

    def test_is_dict_like_with_custom_mapping(self):
        """Test _is_dict_like with custom dict-like object."""
        from rule_interpreter.path_resolver import _is_dict_like

        class CustomMapping:
            def __getitem__(self, key):
                return key
            def keys(self):
                return ["a", "b"]

        assert _is_dict_like(CustomMapping()) is True


class TestGetAttributeEdgeCases:
    """Test _get_attribute with various object types."""

    def test_get_attribute_from_custom_mapping(self):
        """Test _get_attribute for non-dict mappings."""
        from rule_interpreter.path_resolver import _get_attribute

        class CustomMapping:
            def __init__(self):
                self._data = {"key1": "value1", "key2": "value2"}

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        obj = CustomMapping()
        assert _get_attribute(obj, "key1") == "value1"
        assert _get_attribute(obj, "key2") == "value2"

    def test_get_attribute_from_custom_mapping_key_error(self):
        """Test _get_attribute for non-dict mapping with missing key."""
        from rule_interpreter.path_resolver import _get_attribute

        class CustomMapping:
            def __init__(self):
                self._data = {"existing": "value"}

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        obj = CustomMapping()
        with pytest.raises(AttributeError):
            _get_attribute(obj, "missing")

    def test_get_attribute_from_custom_mapping_type_error(self):
        """Test _get_attribute for mapping that raises TypeError."""
        from rule_interpreter.path_resolver import _get_attribute

        class WeirdMapping:
            def __getitem__(self, key):
                raise TypeError("Cannot get item")

            def keys(self):
                return []

        obj = WeirdMapping()
        with pytest.raises(AttributeError):
            _get_attribute(obj, "anything")


class TestGetIndexEdgeCases:
    """Test _get_index edge cases."""

    def test_get_index_non_indexable(self):
        """Test _get_index on non-indexable object."""
        from rule_interpreter.path_resolver import _get_index
        with pytest.raises(TypeError, match="does not support indexing"):
            _get_index(123, 0)

    def test_get_index_on_set(self):
        """Test _get_index on set (has no __getitem__)."""
        from rule_interpreter.path_resolver import _get_index
        with pytest.raises(TypeError, match="does not support indexing"):
            _get_index({1, 2, 3}, 0)


class TestSetAttributeEdgeCases:
    """Test _set_attribute with various object types."""

    def test_set_attribute_on_custom_mapping(self):
        """Test _set_attribute for dict-like objects."""
        from rule_interpreter.path_resolver import _set_attribute

        class CustomMapping:
            def __init__(self):
                self._data = {}

            def __setitem__(self, key, value):
                self._data[key] = value

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        obj = CustomMapping()
        _set_attribute(obj, "new_key", "new_value")
        assert obj["new_key"] == "new_value"


class TestSetIndexEdgeCases:
    """Test _set_index edge cases."""

    def test_set_index_non_settable(self):
        """Test _set_index on object without __setitem__."""
        from rule_interpreter.path_resolver import _set_index
        with pytest.raises(TypeError, match="does not support index assignment"):
            _set_index((1, 2, 3), 0, 99)

    def test_set_index_on_string(self):
        """Test _set_index on immutable string."""
        from rule_interpreter.path_resolver import _set_index
        with pytest.raises(TypeError, match="does not support index assignment"):
            _set_index("hello", 0, "H")


class TestNullSafeAccessEdgeCases:
    """Test null-safe access edge cases."""

    def test_resolve_null_safe_returns_none_on_attribute_error(self):
        """Test null-safe access returning None on AttributeError."""
        entity = {"user": {"name": "John"}}
        resolver = PathResolver(entity)
        result = resolver.resolve(["entity", "user", "missing"], null_safe_indices={2})
        assert result is None

    def test_resolve_null_safe_returns_none_on_key_error(self):
        """Test null-safe access returning None on KeyError."""
        entity = {"data": {"existing": "value"}}
        resolver = PathResolver(entity)
        result = resolver.resolve(["entity", "data", "missing"], null_safe_indices={2})
        assert result is None

    def test_resolve_null_safe_returns_none_on_index_error(self):
        """Test null-safe access returning None on IndexError."""
        entity = {"items": [1, 2, 3]}
        resolver = PathResolver(entity)
        result = resolver.resolve(["entity", "items", 100], null_safe_indices={2})
        assert result is None

    def test_resolve_unknown_identifier_with_context(self):
        """Test unknown identifier when path can't be normalized."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        resolver.add_to_context("other", {"data": 20})

        # With implicit entity, "unknown" becomes ["entity", "unknown"]
        # which will fail when trying to access entity["unknown"]
        with pytest.raises(PathResolutionError):
            resolver.resolve(["unknown"])


class TestPathToString:
    """Test _path_to_string method."""

    def test_path_to_string_empty_path(self):
        """Test _path_to_string with empty path."""
        entity = {"value": 10}
        resolver = PathResolver(entity)
        result = resolver._path_to_string([])
        assert result == ""

    def test_path_to_string_with_int_parts(self):
        """Test _path_to_string with integer indices."""
        entity = {"items": [[1, 2], [3, 4]]}
        resolver = PathResolver(entity)
        result = resolver._path_to_string(["entity", "items", 0, 1])
        assert result == "entity.items[0][1]"

    def test_path_to_string_mixed(self):
        """Test _path_to_string with mixed parts."""
        entity = {}
        resolver = PathResolver(entity)
        result = resolver._path_to_string(["entity", "users", 0, "profile", "scores", -1])
        assert result == "entity.users[0].profile.scores[-1]"


class TestCustomMappingResolution:
    """Test PathResolver with dict-like objects."""

    def test_resolve_through_custom_mapping(self):
        """Test resolving path through a custom dict-like object."""
        class CustomMapping:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        entity = {"config": CustomMapping({"setting": "value"})}
        resolver = PathResolver(entity)
        result = resolver.resolve(["entity", "config", "setting"])
        assert result == "value"

    def test_assign_through_custom_mapping(self):
        """Test assigning through a custom dict-like object."""
        class CustomMapping:
            def __init__(self):
                self._data = {}

            def __getitem__(self, key):
                return self._data[key]

            def __setitem__(self, key, value):
                self._data[key] = value

            def keys(self):
                return self._data.keys()

        mapping = CustomMapping()
        entity = {"config": mapping}
        resolver = PathResolver(entity)
        resolver.assign(["entity", "config", "new_setting"], "new_value")
        assert mapping["new_setting"] == "new_value"

