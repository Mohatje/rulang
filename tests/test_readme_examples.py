"""Example-based tests for rule interpreter features.

These tests verify common usage patterns and real-world scenarios.
They also serve as living documentation for the library's capabilities.
"""

import pytest

from rule_interpreter import RuleEngine, Workflow


class TestBasicRuleChaining:
    """Test basic rule chaining with automatic dependency ordering."""

    def test_quick_start_example(self):
        """Test the basic quick start example."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.age >= 18 => entity.is_adult = true",
            "entity.is_adult == true => entity.discount += 0.1",
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        engine.evaluate(entity)

        assert entity == {"age": 25, "is_adult": True, "discount": 0.1}


class TestStringOperatorExamples:
    """Test string operators: contains, startswith, endswith, matches."""

    def test_contains_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.subject contains "invoice" => ret true'])
        assert engine.evaluate({"subject": "Your invoice #123"}) is True
        assert engine.evaluate({"subject": "Hello world"}) is None

    def test_not_contains_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.subject not contains "spam" => ret true'])
        assert engine.evaluate({"subject": "Hello world"}) is True
        assert engine.evaluate({"subject": "This is spam"}) is None

    def test_startswith_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.email startswith "admin@" => ret true'])
        assert engine.evaluate({"email": "admin@example.com"}) is True
        assert engine.evaluate({"email": "user@example.com"}) is None

    def test_endswith_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.filename endswith ".pdf" => ret true'])
        assert engine.evaluate({"filename": "document.pdf"}) is True
        assert engine.evaluate({"filename": "document.txt"}) is None

    def test_matches_example(self):
        engine = RuleEngine()
        engine.add_rules([r'entity.code matches "INV-\\d{4}" => ret true'])
        assert engine.evaluate({"code": "INV-1234"}) is True
        assert engine.evaluate({"code": "ORD-1234"}) is None


class TestExistenceOperatorExamples:
    """Test existence operators: exists, is_empty."""

    def test_exists_example(self):
        engine = RuleEngine()
        engine.add_rules(["entity.customer_id exists => ret true"])
        assert engine.evaluate({"customer_id": "C123"}) is True
        assert engine.evaluate({"customer_id": None}) is None

    def test_is_empty_example(self):
        engine = RuleEngine()
        engine.add_rules(["entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": ""}) is True
        assert engine.evaluate({"notes": None}) is True
        assert engine.evaluate({"notes": "Some content"}) is None

    def test_not_exists_example(self):
        engine = RuleEngine()
        engine.add_rules(["not entity.email exists => ret true"])
        assert engine.evaluate({"email": None}) is True
        assert engine.evaluate({"email": "test@example.com"}) is None

    def test_not_is_empty_example(self):
        engine = RuleEngine()
        engine.add_rules(["not entity.items is_empty => ret true"])
        assert engine.evaluate({"items": [1, 2, 3]}) is True
        assert engine.evaluate({"items": []}) is None


class TestListOperatorExamples:
    """Test list operators: contains_any, contains_all."""

    def test_contains_any_example(self):
        engine = RuleEngine()
        engine.add_rules([
            'entity.recipients contains_any ["admin@co.com", "support@co.com"] => ret true'
        ])
        assert engine.evaluate({"recipients": ["admin@co.com", "user@co.com"]}) is True
        assert engine.evaluate({"recipients": ["user@co.com", "other@co.com"]}) is None

    def test_contains_all_example(self):
        engine = RuleEngine()
        engine.add_rules([
            'entity.tags contains_all ["reviewed", "approved"] => ret true'
        ])
        assert engine.evaluate({"tags": ["reviewed", "approved", "done"]}) is True
        assert engine.evaluate({"tags": ["reviewed"]}) is None


class TestNullSafeAccessExamples:
    """Test null-safe access (?.) and null coalescing (??) operators."""

    def test_null_safe_access_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.user?.profile?.name == "John" => ret true'])
        assert engine.evaluate({"user": {"profile": {"name": "John"}}}) is True
        assert engine.evaluate({"user": None}) is None

    def test_null_coalescing_example(self):
        engine = RuleEngine()
        engine.add_rules(['entity.nickname ?? "Anonymous" == "Anonymous" => ret true'])
        assert engine.evaluate({"nickname": None}) is True
        assert engine.evaluate({"nickname": "Johnny"}) is None

    def test_combined_null_safe_coalescing(self):
        engine = RuleEngine()
        engine.add_rules(['entity.user?.name ?? "Unknown" == "Unknown" => ret true'])
        assert engine.evaluate({"user": None}) is True
        assert engine.evaluate({"user": {"name": None}}) is True
        assert engine.evaluate({"user": {"name": "John"}}) is None


class TestBuiltinFunctionExamples:
    """Test built-in functions: lower, upper, trim, len, first, last, etc."""

    def test_lower_upper_examples(self):
        engine = RuleEngine()
        engine.add_rules(['lower(entity.name) == "john" => ret true'])
        assert engine.evaluate({"name": "JOHN"}) is True
        assert engine.evaluate({"name": "John"}) is True

        engine.clear()
        engine.add_rules(['upper(entity.code) == "ABC" => ret true'])
        assert engine.evaluate({"code": "abc"}) is True

    def test_trim_example(self):
        engine = RuleEngine()
        engine.add_rules(['trim(entity.input) != "" => ret true'])
        assert engine.evaluate({"input": "  hello  "}) is True
        assert engine.evaluate({"input": "   "}) is None

    def test_len_example(self):
        engine = RuleEngine()
        engine.add_rules(["len(entity.items) > 0 => ret true"])
        assert engine.evaluate({"items": [1, 2, 3]}) is True
        assert engine.evaluate({"items": []}) is None

    def test_first_last_examples(self):
        engine = RuleEngine()
        engine.add_rules(['first(entity.items) == "apple" => ret true'])
        assert engine.evaluate({"items": ["apple", "banana"]}) is True

        engine.clear()
        engine.add_rules(['last(entity.items) == "banana" => ret true'])
        assert engine.evaluate({"items": ["apple", "banana"]}) is True

    def test_int_float_examples(self):
        engine = RuleEngine()
        engine.add_rules(["int(entity.quantity) > 100 => ret true"])
        assert engine.evaluate({"quantity": "150"}) is True
        assert engine.evaluate({"quantity": "50"}) is None

        engine.clear()
        engine.add_rules(["float(entity.amount) >= 99.99 => ret true"])
        assert engine.evaluate({"amount": "100.50"}) is True

    def test_abs_round_examples(self):
        engine = RuleEngine()
        engine.add_rules(["abs(entity.difference) < 10 => ret true"])
        assert engine.evaluate({"difference": -5}) is True
        assert engine.evaluate({"difference": 15}) is None

        engine.clear()
        engine.add_rules(["round(entity.total) == 100 => ret true"])
        assert engine.evaluate({"total": 99.6}) is True
        assert engine.evaluate({"total": 100.4}) is True

    def test_min_max_examples(self):
        engine = RuleEngine()
        engine.add_rules(["min(entity.a, entity.b, entity.c) > 0 => ret true"])
        assert engine.evaluate({"a": 5, "b": 10, "c": 3}) is True
        assert engine.evaluate({"a": 5, "b": 0, "c": 3}) is None

        engine.clear()
        engine.add_rules(["max(entity.x, entity.y) < 100 => ret true"])
        assert engine.evaluate({"x": 50, "y": 75}) is True
        assert engine.evaluate({"x": 50, "y": 150}) is None


class TestAnySatisfiesSemantics:
    """Test any-satisfies semantics for list comparisons."""

    def test_equality_any_satisfies(self):
        """entity.tags == 'urgent' is True if any tag matches."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags == 'urgent' => ret true"])
        assert engine.evaluate({"tags": ["urgent", "finance"]}) is True
        assert engine.evaluate({"tags": ["normal", "finance"]}) is None

    def test_contains_any_satisfies(self):
        """entity.tags contains 'urg' is True if any tag contains substring."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags contains 'urg' => ret true"])
        assert engine.evaluate({"tags": ["urgent", "finance"]}) is True
        assert engine.evaluate({"tags": ["normal", "finance"]}) is None

    def test_startswith_any_satisfies(self):
        """entity.tags startswith 'fin' is True if any tag starts with prefix."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags startswith 'fin' => ret true"])
        assert engine.evaluate({"tags": ["urgent", "finance"]}) is True
        assert engine.evaluate({"tags": ["urgent", "normal"]}) is None

    def test_exact_list_equality(self):
        """When comparing two lists, exact equality is used."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags == ['a', 'b', 'c'] => ret true"])
        assert engine.evaluate({"tags": ["a", "b", "c"]}) is True
        assert engine.evaluate({"tags": ["a", "b"]}) is None
        assert engine.evaluate({"tags": ["c", "b", "a"]}) is None


class TestEmailClassificationScenario:
    """Test email classification scenario with priority routing."""

    def test_email_classification_high_priority(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            r"entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",
            "entity.from_domain not in ['company.com'] and entity.subject contains 'winner' => ret 'spam'",
            "true => ret 'normal'"
        ])

        # High priority
        assert engine.evaluate({
            "subject": "URGENT: Please review",
            "from_domain": "company.com",
            "has_attachments": False,
            "attachments": []
        }) == "high"

    def test_email_classification_invoice_by_pattern(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            r"entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",
            "entity.from_domain not in ['company.com'] and entity.subject contains 'winner' => ret 'spam'",
            "true => ret 'normal'"
        ])

        assert engine.evaluate({
            "subject": "INV-12345 attached",
            "from_domain": "vendor.com",
            "has_attachments": False,
            "attachments": []
        }) == "invoice"

    def test_email_classification_invoice_by_attachment(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            r"entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",
            "entity.from_domain not in ['company.com'] and entity.subject contains 'winner' => ret 'spam'",
            "true => ret 'normal'"
        ])

        assert engine.evaluate({
            "subject": "Document for you",
            "from_domain": "vendor.com",
            "has_attachments": True,
            "attachments": ["report.pdf"]
        }) == "invoice"

    def test_email_classification_spam(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            r"entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",
            "entity.from_domain not in ['company.com'] and lower(entity.subject) contains 'winner' => ret 'spam'",
            "true => ret 'normal'"
        ])

        assert engine.evaluate({
            "subject": "You are a WINNER!",
            "from_domain": "unknown.com",
            "has_attachments": False,
            "attachments": []
        }) == "spam"

    def test_email_classification_normal(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            r"entity.subject matches 'INV-\\d+' or entity.has_attachments and entity.attachments endswith '.pdf' => ret 'invoice'",
            "entity.from_domain not in ['company.com'] and entity.subject contains 'winner' => ret 'spam'",
            "true => ret 'normal'"
        ])

        assert engine.evaluate({
            "subject": "Meeting tomorrow",
            "from_domain": "colleague.com",
            "has_attachments": False,
            "attachments": []
        }) == "normal"


class TestOrderProcessingScenario:
    """Test order processing scenario with discounts and shipping."""

    def test_vip_customer_large_order(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.customer?.membership exists and entity.customer.membership != 'none' => entity.discount = 0.1",
            "entity.subtotal >= 100 => entity.shipping = 0",
            "true => entity.total = (entity.subtotal * (1 - (entity.discount ?? 0))) + (entity.shipping ?? 5.99)",
            "entity.total > 500 => entity.needs_review = true"
        ])

        order = {
            "customer": {"membership": "gold"},
            "subtotal": 600,
            "discount": 0,
            "shipping": 5.99,
            "total": 0,
            "needs_review": False,
        }
        engine.evaluate(order)

        assert order["discount"] == 0.1
        assert order["shipping"] == 0
        assert order["total"] == 540.0  # 600 * 0.9 + 0
        assert order["needs_review"] is True

    def test_guest_small_order(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.customer?.membership exists and entity.customer.membership != 'none' => entity.discount = 0.1",
            "entity.subtotal >= 100 => entity.shipping = 0",
            "true => entity.total = (entity.subtotal * (1 - (entity.discount ?? 0))) + (entity.shipping ?? 5.99)",
            "entity.total > 500 => entity.needs_review = true"
        ])

        order = {
            "customer": None,
            "subtotal": 50,
            "discount": 0,
            "shipping": 5.99,
            "total": 0,
            "needs_review": False,
        }
        engine.evaluate(order)

        assert order["discount"] == 0
        assert order["shipping"] == 5.99
        assert order["total"] == 55.99  # 50 * 1 + 5.99
        assert order["needs_review"] is False


class TestDataValidationScenario:
    """Test data validation scenario with error accumulation."""

    def test_valid_data(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.email is_empty => entity.errors += ['Email is required']",
            "entity.name is_empty => entity.errors += ['Name is required']",
            r"not entity.email is_empty and not entity.email matches '^[^@]+@[^@]+\\.[^@]+$' => entity.errors += ['Invalid email format']",
            "len(entity.name ?? '') > 100 => entity.errors += ['Name too long']",
            "len(entity.errors) == 0 => entity.is_valid = true"
        ])

        entity = {"email": "test@example.com", "name": "John", "errors": [], "is_valid": False}
        engine.evaluate(entity)

        assert entity["errors"] == []
        assert entity["is_valid"] is True

    def test_missing_email(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.email is_empty => entity.errors += ['Email is required']",
            "entity.name is_empty => entity.errors += ['Name is required']",
            r"not entity.email is_empty and not entity.email matches '^[^@]+@[^@]+\\.[^@]+$' => entity.errors += ['Invalid email format']",
            "len(entity.name ?? '') > 100 => entity.errors += ['Name too long']",
            "len(entity.errors) == 0 => entity.is_valid = true"
        ])

        entity = {"email": "", "name": "John", "errors": [], "is_valid": False}
        engine.evaluate(entity)

        assert "Email is required" in entity["errors"]
        assert entity["is_valid"] is False

    def test_invalid_email_format(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.email is_empty => entity.errors += ['Email is required']",
            "entity.name is_empty => entity.errors += ['Name is required']",
            r"not entity.email is_empty and not entity.email matches '^[^@]+@[^@]+\\.[^@]+$' => entity.errors += ['Invalid email format']",
            "len(entity.name ?? '') > 100 => entity.errors += ['Name too long']",
            "len(entity.errors) == 0 => entity.is_valid = true"
        ])

        entity = {"email": "not-an-email", "name": "John", "errors": [], "is_valid": False}
        engine.evaluate(entity)

        assert "Invalid email format" in entity["errors"]
        assert entity["is_valid"] is False


class TestWorkflowExamples:
    """Test workflow integration with rule engine."""

    def test_workflow_decorator_example(self):
        @RuleEngine.workflow("calculate_tax", reads=["entity.subtotal"], writes=["entity.tax"])
        def calculate_tax(entity):
            entity["tax"] = entity["subtotal"] * 0.2

        engine = RuleEngine()
        engine.add_rules(["entity.subtotal > 0 => workflow('calculate_tax')"])

        entity = {"subtotal": 100, "tax": 0}
        engine.evaluate(entity)

        assert entity["tax"] == 20.0

    def test_workflow_wrapper_example(self):
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
        engine.add_rules(["entity.eligible == true => workflow('apply_discount')"])

        entity = {"eligible": True, "subtotal": 100, "total": 0}
        engine.evaluate(entity, workflows=workflows)

        assert entity["total"] == 90.0


class TestEvaluationModeExamples:
    """Test first_match vs all_match evaluation modes."""

    def test_first_match_mode(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "entity.value > 100 => ret 'high'",
            "entity.value > 50 => ret 'medium'",
            "entity.value > 0 => ret 'low'",
        ])

        assert engine.evaluate({"value": 75}) == "medium"

    def test_all_match_mode(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.age >= 18 => entity.is_adult = true",
            "entity.is_adult == true => entity.can_vote = true",
        ])

        entity = {"age": 25, "is_adult": False, "can_vote": False}
        engine.evaluate(entity)

        assert entity["is_adult"] is True
        assert entity["can_vote"] is True


class TestDependencyGraphExamples:
    """Test dependency graph analysis and execution ordering."""

    def test_execution_order(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",  # Rule 0: reads b, writes c
            "entity.a > 0 => entity.b = 1",  # Rule 1: reads a, writes b
        ])

        # Rule 1 executes before Rule 0
        assert engine.get_execution_order() == [1, 0]

    def test_dependency_graph(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",
            "entity.a > 0 => entity.b = 1",
        ])

        # Rule 0 depends on Rule 1
        assert engine.get_dependency_graph() == {1: {0}}
