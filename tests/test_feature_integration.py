"""Integration tests for new features with existing functionality.

Tests comprehensive scenarios combining:
- String operators (contains, startswith, endswith, matches)
- Existence operators (exists, is_empty)
- List operators (contains_any, contains_all)
- Built-in functions (lower, upper, len, etc.)
- Null-safe access (?.) and null coalescing (??)
- Dependency tracking and execution ordering
- Workflows
"""

import pytest

from rule_interpreter import RuleEngine, Workflow


class TestDependencyTrackingWithNewOperators:
    """Test that dependency tracking works correctly with new operators."""

    def test_string_operator_dependency_chain(self):
        """Test dependency chain with string operators."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.email contains '@admin' => entity.is_admin = true",
            "entity.is_admin == true => entity.access = 'full'",
        ])

        assert engine.get_execution_order() == [0, 1]

        entity = {"email": "user@admin.com", "is_admin": False, "access": None}
        engine.evaluate(entity)
        assert entity["is_admin"] is True
        assert entity["access"] == "full"

    def test_function_dependency_chain(self):
        """Test dependency chain with built-in functions."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "len(entity.items) > 0 => entity.has_items = true",
            "entity.has_items == true => entity.status = 'ready'",
        ])

        assert engine.get_execution_order() == [0, 1]

        entity = {"items": [1, 2, 3], "has_items": False, "status": None}
        engine.evaluate(entity)
        assert entity["has_items"] is True
        assert entity["status"] == "ready"

    def test_null_coalescing_dependency_tracking(self):
        """Test that null coalescing tracks both paths."""
        from rule_interpreter.visitor import parse_rule

        rule = parse_rule("entity.primary ?? entity.fallback > 0 => entity.has_value = true")

        # Both paths should be tracked as reads
        assert "entity.primary" in rule.reads
        assert "entity.fallback" in rule.reads
        assert "entity.has_value" in rule.writes

    def test_complex_dependency_resolution(self):
        """Test complex dependency resolution with multiple new operators."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            # Rule 0: Check if user exists
            "entity.user?.email exists => entity.has_user = true",
            # Rule 1: Depends on Rule 0
            "entity.has_user == true and lower(entity.user.email) endswith '@company.com' => entity.is_internal = true",
            # Rule 2: Depends on Rule 1
            "entity.is_internal == true and entity.user?.roles contains_any ['admin', 'manager'] => entity.has_access = true",
        ])

        assert engine.get_execution_order() == [0, 1, 2]

        entity = {
            "user": {"email": "John@COMPANY.COM", "roles": ["admin", "viewer"]},
            "has_user": False,
            "is_internal": False,
            "has_access": False,
        }
        engine.evaluate(entity)
        assert entity["has_user"] is True
        assert entity["is_internal"] is True
        assert entity["has_access"] is True


class TestWorkflowsWithNewOperators:
    """Test workflow integration with new operators."""

    def test_workflow_triggered_by_string_operator(self):
        """Test workflow triggered by contains operator."""
        def process_invoice(entity):
            entity["processed"] = True

        workflows = {
            "process": Workflow(fn=process_invoice, writes=["entity.processed"])
        }

        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.subject contains 'invoice' => workflow('process')",
        ])

        entity = {"subject": "Your invoice #123", "processed": False}
        engine.evaluate(entity, workflows=workflows)
        assert entity["processed"] is True

    def test_workflow_with_null_safe_condition(self):
        """Test workflow with null-safe access in condition."""
        def notify(entity):
            entity["notified"] = True

        workflows = {
            "notify": Workflow(fn=notify, writes=["entity.notified"])
        }

        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.user?.active ?? false == true => workflow('notify')",
        ])

        # With active user
        entity1 = {"user": {"active": True}, "notified": False}
        engine.evaluate(entity1, workflows=workflows)
        assert entity1["notified"] is True

        # With inactive user
        entity2 = {"user": {"active": False}, "notified": False}
        engine.evaluate(entity2, workflows=workflows)
        assert entity2["notified"] is False

        # With null user
        entity3 = {"user": None, "notified": False}
        engine.evaluate(entity3, workflows=workflows)
        assert entity3["notified"] is False

    def test_workflow_dependency_with_new_operators(self):
        """Test workflow dependency ordering with new operators."""
        call_order = []

        def step1(entity):
            call_order.append("step1")
            entity["step1_done"] = True

        def step2(entity):
            call_order.append("step2")
            entity["step2_done"] = True

        workflows = {
            "step1": Workflow(fn=step1, writes=["entity.step1_done"]),
            "step2": Workflow(fn=step2, reads=["entity.step1_done"], writes=["entity.step2_done"]),
        }

        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.data contains 'trigger' => workflow('step1')",
            "entity.step1_done == true => workflow('step2')",
        ])

        entity = {"data": "trigger event", "step1_done": False, "step2_done": False}
        engine.evaluate(entity, workflows=workflows)

        assert call_order == ["step1", "step2"]
        assert entity["step1_done"] is True
        assert entity["step2_done"] is True


class TestCombinedFeatureScenarios:
    """Test complex real-world scenarios combining multiple features."""

    def test_email_classification_scenario(self):
        """Test email classification with all new operators."""
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            # High priority: urgent from known domains
            "lower(entity.subject) contains 'urgent' and entity.from_domain in ['company.com', 'partner.com'] => ret 'high'",
            # Invoice: matches pattern or has PDF attachment
            r"entity.subject matches 'INV-\d+' => ret 'invoice'",
            "entity.attachments exists and entity.attachments endswith '.pdf' => ret 'invoice'",
            # Spam: from unknown domain with suspicious keywords
            "entity.from_domain not in ['company.com'] and lower(entity.subject) contains 'winner' => ret 'spam'",
            # Default
            "true => ret 'normal'",
        ])

        # High priority
        assert engine.evaluate({
            "subject": "URGENT: Please review",
            "from_domain": "company.com",
            "attachments": []
        }) == "high"

        # Invoice by pattern
        assert engine.evaluate({
            "subject": "INV-12345 attached",
            "from_domain": "vendor.com",
            "attachments": []
        }) == "invoice"

        # Invoice by attachment
        assert engine.evaluate({
            "subject": "Document for you",
            "from_domain": "vendor.com",
            "attachments": ["report.pdf"]
        }) == "invoice"

        # Spam
        assert engine.evaluate({
            "subject": "You are a WINNER!",
            "from_domain": "unknown.com",
            "attachments": []
        }) == "spam"

        # Normal
        assert engine.evaluate({
            "subject": "Meeting tomorrow",
            "from_domain": "colleague.com",
            "attachments": []
        }) == "normal"

    def test_order_processing_scenario(self):
        """Test order processing with null-safe access and functions."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            # Apply membership discount
            "entity.customer?.membership exists and entity.customer.membership != 'none' => entity.discount = 0.1",
            # Free shipping for large orders
            "entity.subtotal >= 100 => entity.shipping = 0",
            # Calculate total
            "true => entity.total = (entity.subtotal * (1 - (entity.discount ?? 0))) + (entity.shipping ?? 5.99)",
            # Flag expensive orders
            "entity.total > 500 => entity.needs_review = true",
        ])

        # VIP customer with large order
        order1 = {
            "customer": {"membership": "gold"},
            "subtotal": 600,
            "discount": 0,
            "shipping": 5.99,
            "total": 0,
            "needs_review": False,
        }
        engine.evaluate(order1)
        assert order1["discount"] == 0.1
        assert order1["shipping"] == 0
        assert order1["total"] == 540  # 600 * 0.9 + 0
        assert order1["needs_review"] is True

        # Guest with small order
        order2 = {
            "customer": None,
            "subtotal": 50,
            "discount": 0,
            "shipping": 5.99,
            "total": 0,
            "needs_review": False,
        }
        engine.evaluate(order2)
        assert order2["discount"] == 0
        assert order2["shipping"] == 5.99
        assert order2["total"] == 55.99  # 50 * 1 + 5.99
        assert order2["needs_review"] is False

    def test_data_validation_scenario(self):
        """Test data validation with existence and string operators."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            # Required fields
            "entity.email is_empty => entity.errors += ['Email is required']",
            "entity.name is_empty => entity.errors += ['Name is required']",
            # Email format
            r"not entity.email is_empty and not entity.email matches '^[^@]+@[^@]+\.[^@]+$' => entity.errors += ['Invalid email']",
            # Name length
            "len(entity.name ?? '') > 50 => entity.errors += ['Name too long']",
            # Set validity
            "len(entity.errors) == 0 => entity.is_valid = true",
        ])

        # Valid data
        valid = {"email": "test@example.com", "name": "John", "errors": [], "is_valid": False}
        engine.evaluate(valid)
        assert valid["errors"] == []
        assert valid["is_valid"] is True

        # Invalid email format
        invalid_email = {"email": "not-an-email", "name": "John", "errors": [], "is_valid": False}
        engine.evaluate(invalid_email)
        assert "Invalid email" in invalid_email["errors"]
        assert invalid_email["is_valid"] is False

        # Missing fields
        missing = {"email": "", "name": None, "errors": [], "is_valid": False}
        engine.evaluate(missing)
        assert "Email is required" in missing["errors"]
        assert "Name is required" in missing["errors"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_list_operations(self):
        """Test operations on empty lists."""
        engine = RuleEngine()

        # contains_any with empty list
        engine.clear()
        engine.add_rules(["entity.tags contains_any [] => ret true"])
        assert engine.evaluate({"tags": ["a", "b"]}) is None

        # contains_all with empty list (vacuous truth)
        engine.clear()
        engine.add_rules(["entity.tags contains_all [] => ret true"])
        assert engine.evaluate({"tags": ["a", "b"]}) is True

        # len of empty
        engine.clear()
        engine.add_rules(["len(entity.items) == 0 => ret true"])
        assert engine.evaluate({"items": []}) is True

    def test_deeply_nested_null_safe(self):
        """Test deeply nested null-safe access."""
        engine = RuleEngine()
        engine.add_rules(["entity.a?.b?.c?.d?.e == 'value' => ret true"])

        # Full path exists
        assert engine.evaluate({
            "a": {"b": {"c": {"d": {"e": "value"}}}}
        }) is True

        # Various null points
        assert engine.evaluate({"a": None}) is None
        assert engine.evaluate({"a": {"b": None}}) is None
        assert engine.evaluate({"a": {"b": {"c": None}}}) is None
        assert engine.evaluate({"a": {"b": {"c": {"d": None}}}}) is None

    def test_function_with_null_safe_and_coalescing(self):
        """Test function calls with null-safe and coalescing combined."""
        engine = RuleEngine()
        engine.add_rules([
            "lower(entity.user?.name ?? 'unknown') == 'admin' => ret true"
        ])

        # Name exists
        assert engine.evaluate({"user": {"name": "ADMIN"}}) is True
        assert engine.evaluate({"user": {"name": "user"}}) is None

        # Name is null
        assert engine.evaluate({"user": {"name": None}}) is None  # 'unknown' != 'admin'

        # User is null
        assert engine.evaluate({"user": None}) is None  # 'unknown' != 'admin'

    def test_any_satisfies_with_all_operators(self):
        """Test any-satisfies semantics with various operators."""
        engine = RuleEngine()

        # == any-satisfies
        engine.clear()
        engine.add_rules(["entity.tags == 'a' => ret true"])
        assert engine.evaluate({"tags": ["a", "b", "c"]}) is True
        assert engine.evaluate({"tags": ["b", "c"]}) is None

        # contains any-satisfies
        engine.clear()
        engine.add_rules(["entity.items contains 'test' => ret true"])
        assert engine.evaluate({"items": ["testing", "other"]}) is True
        assert engine.evaluate({"items": ["other", "stuff"]}) is None

        # startswith any-satisfies
        engine.clear()
        engine.add_rules(["entity.emails startswith 'admin' => ret true"])
        assert engine.evaluate({"emails": ["admin@co.com", "user@co.com"]}) is True
        assert engine.evaluate({"emails": ["user@co.com", "other@co.com"]}) is None

    def test_chained_null_coalescing(self):
        """Test chained null coalescing."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.a ?? entity.b ?? entity.c ?? 'default' == 'found' => ret true"
        ])

        assert engine.evaluate({"a": "found", "b": None, "c": None}) is True
        assert engine.evaluate({"a": None, "b": "found", "c": None}) is True
        assert engine.evaluate({"a": None, "b": None, "c": "found"}) is True
        assert engine.evaluate({"a": None, "b": None, "c": None}) is None  # 'default' != 'found'

    def test_mixed_types_in_comparisons(self):
        """Test type handling in comparisons."""
        engine = RuleEngine()

        # String to number comparison via coercion
        engine.clear()
        engine.add_rules(["int(entity.value) > 10 => ret true"])
        assert engine.evaluate({"value": "20"}) is True
        assert engine.evaluate({"value": "5"}) is None

        # Boolean handling
        engine.clear()
        engine.add_rules(["entity.flag ?? false == true => ret true"])
        assert engine.evaluate({"flag": True}) is True
        assert engine.evaluate({"flag": False}) is None
        assert engine.evaluate({"flag": None}) is None


class TestErrorHandlingWithNewOperators:
    """Test error handling for new operators."""

    def test_syntax_error_missing_contains_operand(self):
        """Test syntax error when contains is missing operand."""
        from rule_interpreter import RuleSyntaxError

        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.x contains => ret true"])

    def test_syntax_error_missing_startswith_operand(self):
        """Test syntax error when startswith is missing operand."""
        from rule_interpreter import RuleSyntaxError

        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.x startswith => ret true"])

    def test_syntax_error_missing_null_coalesce_default(self):
        """Test syntax error when ?? is missing default value."""
        from rule_interpreter import RuleSyntaxError

        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.x ?? => ret true"])

    def test_syntax_error_missing_null_safe_property(self):
        """Test syntax error when ?. is missing property."""
        from rule_interpreter import RuleSyntaxError

        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.x?. => ret true"])

    def test_path_resolution_error_without_null_safe(self):
        """Test PathResolutionError when accessing None without null-safe."""
        from rule_interpreter import PathResolutionError

        engine = RuleEngine()
        engine.add_rules(["entity.user.name == 'test' => ret true"])

        with pytest.raises(PathResolutionError):
            engine.evaluate({"user": None})

    def test_null_safe_prevents_path_error(self):
        """Test that null-safe access prevents PathResolutionError."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name == 'test' => ret true"])

        # Should not raise, should return None
        result = engine.evaluate({"user": None})
        assert result is None

    def test_invalid_regex_handled_gracefully(self):
        """Test that invalid regex patterns are handled without crash."""
        engine = RuleEngine()
        engine.add_rules([r"entity.text matches '[invalid' => ret true"])

        # Should not raise, should return None (no match)
        result = engine.evaluate({"text": "anything"})
        assert result is None

    def test_type_coercion_error(self):
        """Test that invalid type coercion raises EvaluationError."""
        from rule_interpreter import EvaluationError

        engine = RuleEngine()
        engine.add_rules(["int(entity.value) > 10 => ret true"])

        with pytest.raises(EvaluationError):
            engine.evaluate({"value": "not a number"})

    def test_none_handling_in_functions(self):
        """Test that functions handle None gracefully."""
        engine = RuleEngine()
        engine.add_rules(["lower(entity.name) == none => ret true"])

        result = engine.evaluate({"name": None})
        assert result is True


class TestAdvancedCombinedFeatures:
    """Test advanced combinations of features."""

    def test_lower_null_safe_contains(self):
        """Test lower() + null-safe + contains combined."""
        engine = RuleEngine()
        engine.add_rules([
            "lower(entity.user?.email ?? '') contains '@admin' => ret 'admin'"
        ])

        assert engine.evaluate({"user": {"email": "User@ADMIN.com"}}) == "admin"
        assert engine.evaluate({"user": {"email": "user@example.com"}}) is None
        assert engine.evaluate({"user": None}) is None

    def test_null_coalescing_in_arithmetic(self):
        """Test null coalescing in arithmetic expressions."""
        engine = RuleEngine()
        engine.add_rules([
            "(entity.price ?? 0) * (entity.quantity ?? 1) > 100 => ret true"
        ])

        assert engine.evaluate({"price": 50, "quantity": 3}) is True  # 150 > 100
        assert engine.evaluate({"price": 50, "quantity": None}) is None  # 50 > 100 is False
        assert engine.evaluate({"price": None, "quantity": 5}) is None  # 0 > 100 is False

    def test_regex_any_satisfies_with_first(self):
        """Test regex + any-satisfies + first() combined."""
        engine = RuleEngine()
        engine.add_rules([
            r"entity.codes matches 'INV-\d{4}' and lower(first(entity.codes) ?? '') startswith 'inv' => ret 'invoice'"
        ])

        assert engine.evaluate({"codes": ["INV-1234", "ORD-5678"]}) == "invoice"
        assert engine.evaluate({"codes": ["ORD-1234", "INV-5678"]}) is None  # first doesn't start with inv
        assert engine.evaluate({"codes": []}) is None

    def test_all_operators_combined_rule(self):
        """Test combining all new operators in one complex rule."""
        engine = RuleEngine()
        engine.add_rules([
            """
            entity.email exists
            and not entity.email is_empty
            and lower(entity.email) endswith '@company.com'
            and entity.roles contains_any ['admin', 'manager']
            and len(entity.permissions ?? []) > 0
            and (entity.status ?? 'pending') == 'active'
            and entity.user?.verified ?? false == true
            => ret 'authorized'
            """
        ])

        # All conditions met
        authorized = {
            "email": "Admin@COMPANY.COM",
            "roles": ["admin", "viewer"],
            "permissions": ["read", "write"],
            "status": "active",
            "user": {"verified": True}
        }
        assert engine.evaluate(authorized) == "authorized"

        # Wrong domain
        wrong_domain = {
            "email": "User@other.com",
            "roles": ["admin"],
            "permissions": ["read"],
            "status": "active",
            "user": {"verified": True}
        }
        assert engine.evaluate(wrong_domain) is None

        # Missing role
        missing_role = {
            "email": "User@company.com",
            "roles": ["viewer"],
            "permissions": ["read"],
            "status": "active",
            "user": {"verified": True}
        }
        assert engine.evaluate(missing_role) is None

        # Not verified
        not_verified = {
            "email": "Admin@company.com",
            "roles": ["admin"],
            "permissions": ["read"],
            "status": "active",
            "user": {"verified": False}
        }
        assert engine.evaluate(not_verified) is None

    def test_list_operators_with_functions_and_existence(self):
        """Test list operators combined with functions and existence checks."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.tags exists and not entity.tags is_empty and entity.tags contains_any ['urgent', 'critical'] => entity.priority = 'high'",
            "entity.priority == 'high' and len(entity.tags) > 2 => entity.needs_review = true",
        ])

        entity = {"tags": ["urgent", "important", "review"], "priority": None, "needs_review": False}
        engine.evaluate(entity)
        assert entity["priority"] == "high"
        assert entity["needs_review"] is True

        # Not enough tags
        entity2 = {"tags": ["urgent", "normal"], "priority": None, "needs_review": False}
        engine.evaluate(entity2)
        assert entity2["priority"] == "high"
        assert entity2["needs_review"] is False

    def test_complex_nested_null_safe_with_functions(self):
        """Test deeply nested null-safe with functions."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "len(entity.order?.items ?? []) > 0 => entity.has_items = true",
            "entity.has_items == true and entity.order?.customer?.vip ?? false == true => entity.priority = 'vip'",
            "entity.has_items == true and entity.priority != 'vip' => entity.priority = 'normal'",
        ])

        # VIP customer
        vip = {
            "order": {"items": [1, 2, 3], "customer": {"vip": True}},
            "has_items": False, "priority": None
        }
        engine.evaluate(vip)
        assert vip["has_items"] is True
        assert vip["priority"] == "vip"

        # Non-VIP
        non_vip = {
            "order": {"items": [1, 2], "customer": {"vip": False}},
            "has_items": False, "priority": None
        }
        engine.evaluate(non_vip)
        assert non_vip["has_items"] is True
        assert non_vip["priority"] == "normal"

        # No order
        no_order = {"order": None, "has_items": False, "priority": None}
        engine.evaluate(no_order)
        assert no_order["has_items"] is False
        assert no_order["priority"] is None


class TestRuleAnalyzerWithNewOperators:
    """Test that rule analyzer correctly extracts reads/writes for new operators."""

    def test_string_operators_reads(self):
        """Test reads extraction for string operators."""
        from rule_interpreter.visitor import parse_rule

        rule = parse_rule("entity.text contains 'test' => entity.found = true")
        assert "entity.text" in rule.reads
        assert "entity.found" in rule.writes

    def test_function_calls_reads(self):
        """Test reads extraction for function calls."""
        from rule_interpreter.visitor import parse_rule

        rule = parse_rule("lower(entity.name) == 'john' => entity.matched = true")
        assert "entity.name" in rule.reads
        assert "entity.matched" in rule.writes

    def test_null_safe_and_coalescing_reads(self):
        """Test reads extraction for null-safe and coalescing."""
        from rule_interpreter.visitor import parse_rule

        rule = parse_rule("entity.a?.b ?? entity.c > 0 => entity.result = true")
        assert "entity.a.b" in rule.reads  # null-safe path
        assert "entity.c" in rule.reads    # fallback path
        assert "entity.result" in rule.writes

    def test_compound_assignment_reads_and_writes(self):
        """Test compound assignment tracks both read and write."""
        from rule_interpreter.visitor import parse_rule

        rule = parse_rule("true => entity.counter += 1")
        assert "entity.counter" in rule.reads
        assert "entity.counter" in rule.writes
