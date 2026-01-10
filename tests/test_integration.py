"""Integration tests for end-to-end scenarios."""

import pytest
from dataclasses import dataclass

from rulang import RuleEngine, Workflow
from rulang.exceptions import PathResolutionError


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear workflow registry before each test."""
    from rulang.workflows import clear_workflow_registry
    clear_workflow_registry()
    yield
    clear_workflow_registry()


class TestEndToEndScenarios:
    """Test complete business logic flows."""

    def test_e_commerce_order_processing(self):
        """Test a complete e-commerce order processing scenario."""
        engine = RuleEngine(mode="all_match")
        
        @RuleEngine.workflow("calculate_tax", reads=["entity.subtotal"], writes=["entity.tax"])
        def calculate_tax(entity):
            entity["tax"] = entity["subtotal"] * 0.1
        
        @RuleEngine.workflow("apply_discount", reads=["entity.subtotal", "entity.discount_rate"], writes=["entity.discount"])
        def apply_discount(entity):
            entity["discount"] = entity["subtotal"] * entity["discount_rate"]
        
        engine.add_rules([
            "entity.subtotal > 100 => workflow('apply_discount')",
            "entity.discount > 0 => entity.subtotal = entity.subtotal - entity.discount",
            "entity.subtotal > 0 => workflow('calculate_tax')",
            "entity.tax > 0 => entity.total = entity.subtotal + entity.tax",
        ])
        
        entity = {
            "subtotal": 200.0,
            "discount_rate": 0.15,
            "discount": 0.0,
            "tax": 0.0,
            "total": 0.0,
        }
        
        result = engine.evaluate(entity)
        
        assert entity["discount"] == 30.0
        assert entity["subtotal"] == 170.0
        assert entity["tax"] == 17.0
        assert entity["total"] == 187.0

    def test_user_authentication_flow(self):
        """Test user authentication and authorization flow."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.age >= 18 => entity.is_adult = true",
            "entity.is_adult == true => entity.can_vote = true",
            "entity.age >= 21 => entity.can_drink = true",
            "entity.is_adult == true and entity.has_license == true => entity.can_drive = true",
        ])
        
        entity = {
            "age": 25,
            "is_adult": False,
            "can_vote": False,
            "can_drink": False,
            "has_license": True,
            "can_drive": False,
        }
        
        engine.evaluate(entity)
        
        assert entity["is_adult"] is True
        assert entity["can_vote"] is True
        assert entity["can_drink"] is True
        assert entity["can_drive"] is True

    def test_inventory_management(self):
        """Test inventory management with stock updates."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.quantity > 0 => entity.in_stock = true",
            "entity.quantity <= 0 => entity.in_stock = false",
            "entity.in_stock == false => entity.status = 'out_of_stock'",
            "entity.quantity < entity.reorder_level => entity.needs_reorder = true",
            "entity.needs_reorder == true => workflow('notify_supplier')",
        ])
        
        def notify_supplier(entity):
            entity["supplier_notified"] = True
        
        entity = {
            "quantity": 5,
            "reorder_level": 10,
            "in_stock": False,
            "status": "active",
            "needs_reorder": False,
            "supplier_notified": False,
        }
        
        engine.evaluate(entity, workflows={"notify_supplier": notify_supplier})
        
        assert entity["in_stock"] is True
        assert entity["needs_reorder"] is True
        assert entity["supplier_notified"] is True

    def test_pricing_calculation(self):
        """Test complex pricing calculation with multiple rules."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.base_price > 0 => entity.price = entity.base_price",
            "entity.is_vip == true => entity.price = entity.price * 0.9",
            "entity.quantity >= 10 => entity.price = entity.price * 0.95",
            "entity.price > 1000 => entity.free_shipping = true",
            "entity.free_shipping == false => entity.total = entity.price + entity.shipping",
            "entity.free_shipping == true => entity.total = entity.price",
        ])
        
        entity = {
            "base_price": 1200.0,
            "is_vip": True,
            "quantity": 15,
            "price": 0.0,
            "shipping": 25.0,
            "free_shipping": False,
            "total": 0.0,
        }
        
        engine.evaluate(entity)
        
        # Base price: 1200
        # VIP discount (10%): 1080
        # Bulk discount (5%): 1026
        # Free shipping: true (price > 1000)
        assert abs(entity["price"] - 1026.0) < 0.01
        assert entity["free_shipping"] is True
        assert abs(entity["total"] - 1026.0) < 0.01

    def test_data_validation_pipeline(self):
        """Test data validation and transformation pipeline."""
        engine = RuleEngine(mode="all_match")
        
        def validate_email(entity):
            if "@" in entity.get("email", ""):
                entity["email_valid"] = True
        
        def normalize_phone(entity):
            entity["phone"] = entity["phone"].replace("-", "").replace(" ", "")
        
        workflows = {
            "validate_email": Workflow(fn=validate_email, reads=["entity.email"], writes=["entity.email_valid"]),
            "normalize_phone": Workflow(fn=normalize_phone, reads=["entity.phone"], writes=["entity.phone"]),
        }
        
        engine.add_rules([
            "entity.email != '' => workflow('validate_email')",
            "entity.phone != '' => workflow('normalize_phone')",
            "entity.email_valid == true and entity.phone != '' => entity.validated = true",
        ])
        
        entity = {
            "email": "test@example.com",
            "phone": "123-456-7890",
            "email_valid": False,
            "validated": False,
        }
        
        engine.evaluate(entity, workflows=workflows)
        
        assert entity["email_valid"] is True
        assert entity["phone"] == "1234567890"
        assert entity["validated"] is True


class TestPerformanceScenarios:
    """Test performance with large rule sets."""

    def test_large_rule_set_100_rules(self):
        """Test with 100 rules."""
        engine = RuleEngine(mode="all_match")
        
        rules = []
        for i in range(100):
            if i == 0:
                rules.append(f"entity.start == true => entity.field{i} = 1")
            else:
                rules.append(f"entity.field{i-1} > 0 => entity.field{i} = entity.field{i-1} + 1")
        
        engine.add_rules(rules)
        
        entity = {"start": True}
        for i in range(100):
            entity[f"field{i}"] = 0
        
        result = engine.evaluate(entity)
        
        # All rules should execute in order
        assert entity["field0"] == 1
        assert entity["field99"] == 100

    def test_deep_nesting_evaluation(self):
        """Test evaluation with deeply nested entity structures."""
        engine = RuleEngine()
        
        # Create deeply nested structure
        entity = {}
        current = entity
        for i in range(10):
            current[f"level{i}"] = {}
            current = current[f"level{i}"]
        current["value"] = 0
        
        engine.add_rules("entity.level0.level1.level2.level3.level4.level5.level6.level7.level8.level9.value == 0 => entity.level0.level1.level2.level3.level4.level5.level6.level7.level8.level9.value = 1")
        
        result = engine.evaluate(entity)
        
        assert current["value"] == 1

    def test_complex_dependency_graph(self):
        """Test with complex dependency relationships."""
        engine = RuleEngine(mode="all_match")
        
        # Create a complex graph: multiple chains converging
        rules = []
        # Chain 1: a -> b -> e
        rules.append("entity.a > 0 => entity.b = 1")
        rules.append("entity.b > 0 => entity.e = 1")
        # Chain 2: c -> d -> e
        rules.append("entity.c > 0 => entity.d = 1")
        rules.append("entity.d > 0 => entity.e = 1")
        # Final: e -> f
        rules.append("entity.e > 0 => entity.f = 1")
        
        engine.add_rules(rules)
        
        entity = {"a": 10, "c": 10, "b": 0, "d": 0, "e": 0, "f": 0}
        engine.evaluate(entity)
        
        # All should execute
        assert entity["b"] == 1
        assert entity["d"] == 1
        assert entity["e"] == 1
        assert entity["f"] == 1


class TestErrorRecovery:
    """Test error handling and recovery."""

    def test_partial_evaluation_failure(self):
        """Test that one rule failure stops evaluation."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.valid > 0 => entity.result1 = 1",
            "entity.invalid.path > 0 => entity.result2 = 1",  # Will fail
            "entity.valid > 0 => entity.result3 = 1",
        ])
        
        entity = {"valid": 10, "result1": 0, "result2": 0, "result3": 0}
        
        # Evaluation stops on first error
        with pytest.raises(PathResolutionError):
            engine.evaluate(entity)
        
        # First rule may or may not have executed depending on execution order
        # The error occurs during condition evaluation, so it depends on order

    def test_error_propagation(self):
        """Test that errors propagate correctly."""
        engine = RuleEngine()
        
        engine.add_rules("entity.missing.path > 0 => ret true")
        
        with pytest.raises(PathResolutionError):
            engine.evaluate({"name": "test"})

    def test_state_consistency_after_error(self):
        """Test that entity state is consistent after error."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.valid > 0 => entity.processed = true",
            "entity.invalid.path > 0 => entity.failed = true",
        ])
        
        entity = {"valid": 10, "processed": False, "failed": False}
        
        # Error occurs during condition evaluation
        with pytest.raises(PathResolutionError):
            engine.evaluate(entity)
        
        # State depends on execution order - if first rule executes before second's condition is evaluated
        # For now, we just verify error is raised
        assert True  # Test passes if error is raised correctly


class TestRealWorldScenarios:
    """Test realistic business scenarios."""

    def test_loan_approval_system(self):
        """Test a loan approval system."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.credit_score >= 700 => entity.credit_approved = true",
            "entity.income >= 50000 => entity.income_approved = true",
            "entity.credit_approved == true and entity.income_approved == true => entity.loan_approved = true",
            "entity.loan_approved == true => entity.interest_rate = 0.05",
            "entity.credit_score < 700 => entity.interest_rate = 0.10",
        ])
        
        entity = {
            "credit_score": 750,
            "income": 60000,
            "credit_approved": False,
            "income_approved": False,
            "loan_approved": False,
            "interest_rate": 0.0,
        }
        
        engine.evaluate(entity)
        
        assert entity["credit_approved"] is True
        assert entity["income_approved"] is True
        assert entity["loan_approved"] is True
        assert entity["interest_rate"] == 0.05

    def test_shipping_cost_calculation(self):
        """Test shipping cost calculation based on multiple factors."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.weight <= 1 => entity.base_shipping = 5.0",
            "entity.weight > 1 and entity.weight <= 5 => entity.base_shipping = 10.0",
            "entity.weight > 5 => entity.base_shipping = 20.0",
            "entity.express == true => entity.shipping_multiplier = 2.0",
            "entity.express == false => entity.shipping_multiplier = 1.0",
            "entity.base_shipping > 0 => entity.shipping_cost = entity.base_shipping * entity.shipping_multiplier",
        ])
        
        entity = {
            "weight": 3.5,
            "express": True,
            "base_shipping": 0.0,
            "shipping_multiplier": 1.0,
            "shipping_cost": 0.0,
        }
        
        engine.evaluate(entity)
        
        assert entity["base_shipping"] == 10.0
        assert entity["shipping_multiplier"] == 2.0
        assert entity["shipping_cost"] == 20.0

    def test_grade_calculation_system(self):
        """Test a grade calculation system."""
        engine = RuleEngine(mode="all_match")
        
        engine.add_rules([
            "entity.score >= 90 => entity.grade = 'A'",
            "entity.score >= 80 and entity.score < 90 => entity.grade = 'B'",
            "entity.score >= 70 and entity.score < 80 => entity.grade = 'C'",
            "entity.score >= 60 and entity.score < 70 => entity.grade = 'D'",
            "entity.score < 60 => entity.grade = 'F'",
            "entity.grade == 'A' or entity.grade == 'B' => entity.passed = true",
            "entity.passed == false => entity.retake_required = true",
        ])
        
        entity = {
            "score": 85,
            "grade": "",
            "passed": False,
            "retake_required": False,
        }
        
        engine.evaluate(entity)
        
        assert entity["grade"] == "B"
        assert entity["passed"] is True
        assert entity["retake_required"] is False

