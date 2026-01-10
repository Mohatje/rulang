"""Tests for string operators: contains, startswith, endswith, matches."""

import pytest

from rulang import RuleEngine


class TestContainsOperator:
    """Tests for the 'contains' operator (substring check)."""

    def test_contains_basic(self):
        """Test basic substring matching."""
        engine = RuleEngine()
        engine.add_rules(["entity.text contains 'hello' => ret true"])
        assert engine.evaluate({"text": "hello world"}) is True
        assert engine.evaluate({"text": "world"}) is None

    def test_contains_case_sensitive(self):
        """Test that contains is case-sensitive."""
        engine = RuleEngine()
        engine.add_rules(["entity.text contains 'Hello' => ret true"])
        assert engine.evaluate({"text": "Hello world"}) is True
        assert engine.evaluate({"text": "hello world"}) is None

    def test_contains_with_lower(self):
        """Test case-insensitive contains using lower()."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.text) contains 'hello' => ret true"])
        assert engine.evaluate({"text": "Hello World"}) is True
        assert engine.evaluate({"text": "HELLO"}) is True
        assert engine.evaluate({"text": "world"}) is None

    def test_contains_empty_string(self):
        """Test contains with empty string (always true)."""
        engine = RuleEngine()
        engine.add_rules(["entity.text contains '' => ret true"])
        assert engine.evaluate({"text": "anything"}) is True
        assert engine.evaluate({"text": ""}) is True

    def test_contains_with_list_any_satisfies(self):
        """Test contains with list field (any-satisfies semantics)."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags contains 'urg' => ret true"])
        assert engine.evaluate({"tags": ["urgent", "important"]}) is True
        assert engine.evaluate({"tags": ["low", "priority"]}) is None

    def test_contains_with_none(self):
        """Test contains with None values."""
        engine = RuleEngine()
        engine.add_rules(["entity.text contains 'test' => ret true"])
        assert engine.evaluate({"text": None}) is None


class TestNotContainsOperator:
    """Tests for the 'not contains' operator."""

    def test_not_contains_basic(self):
        """Test basic not contains."""
        engine = RuleEngine()
        engine.add_rules(["entity.text not contains 'spam' => ret true"])
        assert engine.evaluate({"text": "hello world"}) is True
        assert engine.evaluate({"text": "spam message"}) is None

    def test_not_contains_with_list(self):
        """Test not contains with list (none satisfy)."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags not contains 'spam' => ret true"])
        assert engine.evaluate({"tags": ["good", "content"]}) is True
        assert engine.evaluate({"tags": ["spam", "bad"]}) is None


class TestStartsWithOperator:
    """Tests for the 'startswith' operator."""

    def test_startswith_basic(self):
        """Test basic prefix matching."""
        engine = RuleEngine()
        engine.add_rules(["entity.email startswith 'admin@' => ret true"])
        assert engine.evaluate({"email": "admin@example.com"}) is True
        assert engine.evaluate({"email": "user@example.com"}) is None

    def test_starts_with_alias(self):
        """Test starts_with alias."""
        engine = RuleEngine()
        engine.add_rules(["entity.email starts_with 'admin@' => ret true"])
        assert engine.evaluate({"email": "admin@example.com"}) is True

    def test_startswith_case_sensitive(self):
        """Test that startswith is case-sensitive."""
        engine = RuleEngine()
        engine.add_rules(["entity.email startswith 'Admin@' => ret true"])
        assert engine.evaluate({"email": "Admin@example.com"}) is True
        assert engine.evaluate({"email": "admin@example.com"}) is None

    def test_startswith_with_lower(self):
        """Test case-insensitive startswith using lower()."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.email) startswith 'admin@' => ret true"])
        assert engine.evaluate({"email": "ADMIN@example.com"}) is True
        assert engine.evaluate({"email": "Admin@example.com"}) is True

    def test_startswith_with_list_any_satisfies(self):
        """Test startswith with list field (any-satisfies semantics)."""
        engine = RuleEngine()
        engine.add_rules(["entity.domains startswith 'admin' => ret true"])
        assert engine.evaluate({"domains": ["admin.com", "user.com"]}) is True
        assert engine.evaluate({"domains": ["user.com", "test.com"]}) is None

    def test_startswith_with_none(self):
        """Test startswith with None values."""
        engine = RuleEngine()
        engine.add_rules(["entity.text startswith 'test' => ret true"])
        assert engine.evaluate({"text": None}) is None


class TestEndsWithOperator:
    """Tests for the 'endswith' operator."""

    def test_endswith_basic(self):
        """Test basic suffix matching."""
        engine = RuleEngine()
        engine.add_rules(["entity.filename endswith '.pdf' => ret true"])
        assert engine.evaluate({"filename": "document.pdf"}) is True
        assert engine.evaluate({"filename": "document.txt"}) is None

    def test_ends_with_alias(self):
        """Test ends_with alias."""
        engine = RuleEngine()
        engine.add_rules(["entity.filename ends_with '.pdf' => ret true"])
        assert engine.evaluate({"filename": "document.pdf"}) is True

    def test_endswith_case_sensitive(self):
        """Test that endswith is case-sensitive."""
        engine = RuleEngine()
        engine.add_rules(["entity.filename endswith '.PDF' => ret true"])
        assert engine.evaluate({"filename": "document.PDF"}) is True
        assert engine.evaluate({"filename": "document.pdf"}) is None

    def test_endswith_with_lower(self):
        """Test case-insensitive endswith using lower()."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.filename) endswith '.pdf' => ret true"])
        assert engine.evaluate({"filename": "document.PDF"}) is True
        assert engine.evaluate({"filename": "document.Pdf"}) is True

    def test_endswith_with_list_any_satisfies(self):
        """Test endswith with list field (any-satisfies semantics)."""
        engine = RuleEngine()
        engine.add_rules(["entity.files endswith '.pdf' => ret true"])
        assert engine.evaluate({"files": ["doc.pdf", "img.png"]}) is True
        assert engine.evaluate({"files": ["doc.txt", "img.png"]}) is None

    def test_endswith_with_none(self):
        """Test endswith with None values."""
        engine = RuleEngine()
        engine.add_rules(["entity.text endswith 'test' => ret true"])
        assert engine.evaluate({"text": None}) is None


class TestMatchesOperator:
    """Tests for the 'matches' operator (regex matching)."""

    def test_matches_basic(self):
        """Test basic regex matching."""
        engine = RuleEngine()
        engine.add_rules([r"entity.code matches 'INV-\\d{4}' => ret true"])
        assert engine.evaluate({"code": "INV-1234"}) is True
        assert engine.evaluate({"code": "INV-12"}) is None
        assert engine.evaluate({"code": "ORDER-1234"}) is None

    def test_matches_email_pattern(self):
        """Test regex matching for email-like pattern."""
        engine = RuleEngine()
        engine.add_rules([r"entity.email matches '^[a-z]+@[a-z]+\\.[a-z]+$' => ret true"])
        assert engine.evaluate({"email": "user@example.com"}) is True
        assert engine.evaluate({"email": "invalid-email"}) is None

    def test_matches_partial(self):
        """Test that matches does partial matching (search, not fullmatch)."""
        engine = RuleEngine()
        engine.add_rules([r"entity.text matches '\\d+' => ret true"])
        assert engine.evaluate({"text": "Order #123"}) is True
        assert engine.evaluate({"text": "No numbers"}) is None

    def test_matches_with_list_any_satisfies(self):
        """Test matches with list field (any-satisfies semantics)."""
        engine = RuleEngine()
        engine.add_rules([r"entity.codes matches 'INV-\\d+' => ret true"])
        assert engine.evaluate({"codes": ["INV-123", "ORD-456"]}) is True
        assert engine.evaluate({"codes": ["ORD-123", "REF-456"]}) is None

    def test_matches_invalid_regex(self):
        """Test matches with invalid regex pattern (should return False)."""
        engine = RuleEngine()
        engine.add_rules([r"entity.text matches '[invalid' => ret true"])
        assert engine.evaluate({"text": "anything"}) is None

    def test_matches_with_none(self):
        """Test matches with None values."""
        engine = RuleEngine()
        engine.add_rules([r"entity.text matches '\\d+' => ret true"])
        assert engine.evaluate({"text": None}) is None


class TestCombinedStringOperators:
    """Tests for combining string operators with other conditions."""

    def test_contains_and_startswith(self):
        """Test combining contains and startswith."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.email startswith 'admin' and entity.email contains '@example' => ret true"
        ])
        assert engine.evaluate({"email": "admin@example.com"}) is True
        assert engine.evaluate({"email": "admin@other.com"}) is None
        assert engine.evaluate({"email": "user@example.com"}) is None

    def test_not_contains_or_endswith(self):
        """Test combining not contains and endswith."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.filename not contains 'temp' or entity.filename endswith '.pdf' => ret true"
        ])
        assert engine.evaluate({"filename": "document.pdf"}) is True
        assert engine.evaluate({"filename": "temp_file.pdf"}) is True
        assert engine.evaluate({"filename": "report.txt"}) is True
        assert engine.evaluate({"filename": "temp_file.txt"}) is None

    def test_matches_with_assignment(self):
        """Test regex matching with action assignment."""
        engine = RuleEngine()
        engine.add_rules([
            r"entity.code matches 'INV-\\d+' => entity.category = 'invoice'"
        ])
        entity = {"code": "INV-1234", "category": None}
        engine.evaluate(entity)
        assert entity["category"] == "invoice"
