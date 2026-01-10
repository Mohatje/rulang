"""Tests for built-in functions: lower, upper, trim, len, int, float, str, bool, etc."""

import pytest

from rulang import RuleEngine


class TestStringFunctions:
    """Tests for string transformation functions."""

    def test_lower_basic(self):
        """Test lower() function."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.name) == 'john' => ret true"])
        assert engine.evaluate({"name": "JOHN"}) is True
        assert engine.evaluate({"name": "John"}) is True
        assert engine.evaluate({"name": "john"}) is True
        assert engine.evaluate({"name": "Jane"}) is None

    def test_lower_with_none(self):
        """Test lower() with None value."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.name) == none => ret true"])
        assert engine.evaluate({"name": None}) is True

    def test_upper_basic(self):
        """Test upper() function."""
        engine = RuleEngine()
        engine.add_rules(["upper(entity.code) == 'ABC' => ret true"])
        assert engine.evaluate({"code": "abc"}) is True
        assert engine.evaluate({"code": "Abc"}) is True
        assert engine.evaluate({"code": "ABC"}) is True

    def test_trim_basic(self):
        """Test trim() function."""
        engine = RuleEngine()
        engine.add_rules(["trim(entity.text) == 'hello' => ret true"])
        assert engine.evaluate({"text": "  hello  "}) is True
        assert engine.evaluate({"text": "hello"}) is True
        assert engine.evaluate({"text": "\thello\n"}) is True

    def test_strip_alias(self):
        """Test strip() as alias for trim()."""
        engine = RuleEngine()
        engine.add_rules(["strip(entity.text) == 'hello' => ret true"])
        assert engine.evaluate({"text": "  hello  "}) is True

    def test_lower_in_contains(self):
        """Test lower() combined with contains."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.subject) contains 'urgent' => ret true"])
        assert engine.evaluate({"subject": "URGENT: Please review"}) is True
        assert engine.evaluate({"subject": "Urgent request"}) is True
        assert engine.evaluate({"subject": "Normal message"}) is None


class TestCollectionFunctions:
    """Tests for collection functions."""

    def test_len_list(self):
        """Test len() on lists."""
        engine = RuleEngine()
        engine.add_rules(["len(entity.items) > 0 => ret true"])
        assert engine.evaluate({"items": [1, 2, 3]}) is True
        assert engine.evaluate({"items": []}) is None

    def test_len_string(self):
        """Test len() on strings."""
        engine = RuleEngine()
        engine.add_rules(["len(entity.name) > 5 => ret true"])
        assert engine.evaluate({"name": "Jonathan"}) is True
        assert engine.evaluate({"name": "John"}) is None

    def test_len_with_none(self):
        """Test len() with None (returns 0)."""
        engine = RuleEngine()
        engine.add_rules(["len(entity.items) == 0 => ret true"])
        assert engine.evaluate({"items": None}) is True

    def test_len_dict(self):
        """Test len() on dictionaries."""
        engine = RuleEngine()
        engine.add_rules(["len(entity.meta) == 2 => ret true"])
        assert engine.evaluate({"meta": {"a": 1, "b": 2}}) is True
        assert engine.evaluate({"meta": {"a": 1}}) is None

    def test_first_basic(self):
        """Test first() function."""
        engine = RuleEngine()
        engine.add_rules(["first(entity.items) == 'apple' => ret true"])
        assert engine.evaluate({"items": ["apple", "banana"]}) is True
        assert engine.evaluate({"items": ["banana", "apple"]}) is None

    def test_first_empty(self):
        """Test first() on empty list."""
        engine = RuleEngine()
        engine.add_rules(["first(entity.items) == none => ret true"])
        assert engine.evaluate({"items": []}) is True

    def test_last_basic(self):
        """Test last() function."""
        engine = RuleEngine()
        engine.add_rules(["last(entity.items) == 'banana' => ret true"])
        assert engine.evaluate({"items": ["apple", "banana"]}) is True
        assert engine.evaluate({"items": ["banana", "apple"]}) is None

    def test_last_empty(self):
        """Test last() on empty list."""
        engine = RuleEngine()
        engine.add_rules(["last(entity.items) == none => ret true"])
        assert engine.evaluate({"items": []}) is True

    def test_keys_basic(self):
        """Test keys() function."""
        engine = RuleEngine()
        engine.add_rules(["'name' in keys(entity.data) => ret true"])
        assert engine.evaluate({"data": {"name": "John", "age": 30}}) is True
        assert engine.evaluate({"data": {"age": 30}}) is None

    def test_values_basic(self):
        """Test values() function."""
        engine = RuleEngine()
        engine.add_rules(["'John' in values(entity.data) => ret true"])
        assert engine.evaluate({"data": {"name": "John", "age": 30}}) is True
        assert engine.evaluate({"data": {"name": "Jane"}}) is None


class TestTypeCoercionFunctions:
    """Tests for type coercion functions."""

    def test_int_from_string(self):
        """Test int() from string."""
        engine = RuleEngine()
        engine.add_rules(["int(entity.quantity) > 100 => ret true"])
        assert engine.evaluate({"quantity": "150"}) is True
        assert engine.evaluate({"quantity": "50"}) is None

    def test_int_from_float(self):
        """Test int() from float."""
        engine = RuleEngine()
        engine.add_rules(["int(entity.price) == 99 => ret true"])
        assert engine.evaluate({"price": 99.99}) is True

    def test_int_with_none(self):
        """Test int() with None."""
        engine = RuleEngine()
        engine.add_rules(["int(entity.value) == none => ret true"])
        assert engine.evaluate({"value": None}) is True

    def test_float_from_string(self):
        """Test float() from string."""
        engine = RuleEngine()
        engine.add_rules(["float(entity.price) >= 99.99 => ret true"])
        assert engine.evaluate({"price": "99.99"}) is True
        assert engine.evaluate({"price": "100.50"}) is True
        assert engine.evaluate({"price": "50.00"}) is None

    def test_float_from_int(self):
        """Test float() from int."""
        engine = RuleEngine()
        engine.add_rules(["float(entity.value) == 100.0 => ret true"])
        assert engine.evaluate({"value": 100}) is True

    def test_str_from_number(self):
        """Test str() from number."""
        engine = RuleEngine()
        engine.add_rules(["str(entity.code) == '123' => ret true"])
        assert engine.evaluate({"code": 123}) is True

    def test_bool_truthy(self):
        """Test bool() with truthy values."""
        engine = RuleEngine()
        engine.add_rules(["bool(entity.value) == true => ret true"])
        assert engine.evaluate({"value": 1}) is True
        assert engine.evaluate({"value": "yes"}) is True
        assert engine.evaluate({"value": [1, 2]}) is True

    def test_bool_falsy(self):
        """Test bool() with falsy values."""
        engine = RuleEngine()
        engine.add_rules(["bool(entity.value) == false => ret true"])
        assert engine.evaluate({"value": 0}) is True
        assert engine.evaluate({"value": ""}) is True
        assert engine.evaluate({"value": []}) is True


class TestMathFunctions:
    """Tests for math functions."""

    def test_abs_positive(self):
        """Test abs() with positive number."""
        engine = RuleEngine()
        engine.add_rules(["abs(entity.value) == 10 => ret true"])
        assert engine.evaluate({"value": 10}) is True

    def test_abs_negative(self):
        """Test abs() with negative number."""
        engine = RuleEngine()
        engine.add_rules(["abs(entity.value) == 10 => ret true"])
        assert engine.evaluate({"value": -10}) is True

    def test_round_basic(self):
        """Test round() function."""
        engine = RuleEngine()
        engine.add_rules(["round(entity.price, 2) == 99.99 => ret true"])
        assert engine.evaluate({"price": 99.994}) is True
        # Note: 99.985 rounds to 99.98 due to banker's rounding (round half to even)
        assert engine.evaluate({"price": 99.986}) is True

    def test_round_no_decimals(self):
        """Test round() with no decimal places."""
        engine = RuleEngine()
        engine.add_rules(["round(entity.price) == 100 => ret true"])
        assert engine.evaluate({"price": 99.5}) is True
        assert engine.evaluate({"price": 100.4}) is True

    def test_min_function(self):
        """Test min() function."""
        engine = RuleEngine()
        engine.add_rules(["min(entity.a, entity.b, entity.c) == 1 => ret true"])
        assert engine.evaluate({"a": 3, "b": 1, "c": 2}) is True

    def test_max_function(self):
        """Test max() function."""
        engine = RuleEngine()
        engine.add_rules(["max(entity.a, entity.b, entity.c) == 3 => ret true"])
        assert engine.evaluate({"a": 3, "b": 1, "c": 2}) is True


class TestTypeCheckingFunctions:
    """Tests for type checking functions."""

    def test_is_list_true(self):
        """Test is_list() returns true for lists."""
        engine = RuleEngine()
        engine.add_rules(["is_list(entity.items) == true => ret true"])
        assert engine.evaluate({"items": [1, 2, 3]}) is True
        assert engine.evaluate({"items": ()}) is True  # Tuples count too

    def test_is_list_false(self):
        """Test is_list() returns false for non-lists."""
        engine = RuleEngine()
        engine.add_rules(["is_list(entity.items) == false => ret true"])
        assert engine.evaluate({"items": "not a list"}) is True
        assert engine.evaluate({"items": 123}) is True

    def test_is_string_true(self):
        """Test is_string() returns true for strings."""
        engine = RuleEngine()
        engine.add_rules(["is_string(entity.name) == true => ret true"])
        assert engine.evaluate({"name": "John"}) is True
        assert engine.evaluate({"name": ""}) is True

    def test_is_string_false(self):
        """Test is_string() returns false for non-strings."""
        engine = RuleEngine()
        engine.add_rules(["is_string(entity.value) == false => ret true"])
        assert engine.evaluate({"value": 123}) is True
        assert engine.evaluate({"value": [1, 2]}) is True

    def test_is_number_true(self):
        """Test is_number() returns true for numbers."""
        engine = RuleEngine()
        engine.add_rules(["is_number(entity.value) == true => ret true"])
        assert engine.evaluate({"value": 123}) is True
        assert engine.evaluate({"value": 3.14}) is True

    def test_is_number_false(self):
        """Test is_number() returns false for non-numbers."""
        engine = RuleEngine()
        engine.add_rules(["is_number(entity.value) == false => ret true"])
        assert engine.evaluate({"value": "123"}) is True
        assert engine.evaluate({"value": None}) is True

    def test_is_none_true(self):
        """Test is_none() returns true for None."""
        engine = RuleEngine()
        engine.add_rules(["is_none(entity.value) == true => ret true"])
        assert engine.evaluate({"value": None}) is True

    def test_is_none_false(self):
        """Test is_none() returns false for non-None."""
        engine = RuleEngine()
        engine.add_rules(["is_none(entity.value) == false => ret true"])
        assert engine.evaluate({"value": ""}) is True
        assert engine.evaluate({"value": 0}) is True
        assert engine.evaluate({"value": False}) is True


class TestNestedFunctionCalls:
    """Tests for nested function calls."""

    def test_lower_of_trim(self):
        """Test lower(trim(x))."""
        engine = RuleEngine()
        engine.add_rules(["lower(trim(entity.text)) == 'hello' => ret true"])
        assert engine.evaluate({"text": "  HELLO  "}) is True

    def test_len_of_trim(self):
        """Test len(trim(x))."""
        engine = RuleEngine()
        engine.add_rules(["len(trim(entity.text)) == 5 => ret true"])
        assert engine.evaluate({"text": "  hello  "}) is True

    def test_int_of_abs(self):
        """Test int(abs(x))."""
        engine = RuleEngine()
        engine.add_rules(["int(abs(entity.value)) == 10 => ret true"])
        assert engine.evaluate({"value": -10.5}) is True

    def test_first_of_keys(self):
        """Test first(keys(x))."""
        engine = RuleEngine()
        # Note: dict key order is preserved in Python 3.7+
        engine.add_rules(["first(keys(entity.data)) exists => ret true"])
        assert engine.evaluate({"data": {"name": "John"}}) is True


class TestFunctionWithOperators:
    """Tests for functions combined with operators."""

    def test_lower_contains(self):
        """Test lower() with contains operator."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.email) contains '@example' => ret true"])
        assert engine.evaluate({"email": "User@EXAMPLE.com"}) is True

    def test_len_comparison(self):
        """Test len() with comparison operators."""
        engine = RuleEngine()
        engine.add_rules([
            "len(entity.items) >= 3 => entity.size = 'large'",
            "len(entity.items) < 3 => entity.size = 'small'"
        ])
        entity1 = {"items": [1, 2, 3, 4], "size": None}
        engine.evaluate(entity1)
        assert entity1["size"] == "large"

        entity2 = {"items": [1], "size": None}
        engine.evaluate(entity2)
        assert entity2["size"] == "small"

    def test_function_in_assignment(self):
        """Test function call in assignment."""
        engine = RuleEngine()
        engine.add_rules(["true => entity.name_lower = lower(entity.name)"])
        entity = {"name": "JOHN", "name_lower": None}
        engine.evaluate(entity)
        assert entity["name_lower"] == "john"

    def test_arithmetic_with_functions(self):
        """Test functions with arithmetic."""
        engine = RuleEngine()
        engine.add_rules(["len(entity.a) + len(entity.b) > 5 => ret true"])
        assert engine.evaluate({"a": [1, 2, 3], "b": [4, 5, 6]}) is True
        assert engine.evaluate({"a": [1], "b": [2]}) is None
