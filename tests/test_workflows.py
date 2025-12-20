"""Tests for the workflow system."""

import pytest

from rule_interpreter.workflows import (
    Workflow,
    workflow,
    get_registered_workflows,
    clear_workflow_registry,
    merge_workflows,
)


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear workflow registry before and after each test."""
    clear_workflow_registry()
    yield
    clear_workflow_registry()


class TestWorkflowClass:
    """Test the Workflow wrapper class."""

    def test_workflow_creation(self):
        def my_fn(entity):
            return entity["value"] * 2

        wf = Workflow(fn=my_fn, reads=["entity.value"], writes=["entity.result"])

        assert wf.fn == my_fn
        assert wf.reads == ["entity.value"]
        assert wf.writes == ["entity.result"]

    def test_workflow_callable(self):
        def double(entity):
            return entity["value"] * 2

        wf = Workflow(fn=double, reads=["entity.value"], writes=[])

        result = wf({"value": 10})
        assert result == 20

    def test_workflow_default_empty_lists(self):
        wf = Workflow(fn=lambda e: None)

        assert wf.reads == []
        assert wf.writes == []


class TestWorkflowDecorator:
    """Test the @workflow decorator."""

    def test_basic_registration(self):
        @workflow("my_workflow")
        def my_fn(entity):
            pass

        registry = get_registered_workflows()
        assert "my_workflow" in registry
        assert registry["my_workflow"].fn == my_fn

    def test_registration_with_dependencies(self):
        @workflow("calculate", reads=["entity.input"], writes=["entity.output"])
        def calculate(entity):
            entity["output"] = entity["input"] * 2

        registry = get_registered_workflows()
        wf = registry["calculate"]

        assert wf.reads == ["entity.input"]
        assert wf.writes == ["entity.output"]

    def test_decorator_preserves_function(self):
        @workflow("test")
        def my_fn(entity):
            return "result"

        # The decorated function should still be callable
        assert my_fn({"value": 1}) == "result"

    def test_multiple_registrations(self):
        @workflow("first")
        def first(e):
            pass

        @workflow("second")
        def second(e):
            pass

        registry = get_registered_workflows()
        assert "first" in registry
        assert "second" in registry


class TestWorkflowRegistry:
    """Test workflow registry functions."""

    def test_clear_registry(self):
        @workflow("test")
        def test_fn(e):
            pass

        assert len(get_registered_workflows()) > 0

        clear_workflow_registry()

        assert len(get_registered_workflows()) == 0

    def test_get_registered_workflows_returns_copy(self):
        @workflow("test")
        def test_fn(e):
            pass

        registry1 = get_registered_workflows()
        registry2 = get_registered_workflows()

        assert registry1 is not registry2
        assert registry1 == registry2


class TestMergeWorkflows:
    """Test workflow merging functionality."""

    def test_merge_with_none(self):
        @workflow("registered")
        def registered_fn(e):
            pass

        result = merge_workflows(None)

        assert "registered" in result

    def test_merge_with_passed_workflows(self):
        @workflow("registered")
        def registered_fn(e):
            pass

        def passed_fn(e):
            pass

        result = merge_workflows({"passed": passed_fn})

        assert "registered" in result
        assert "passed" in result

    def test_passed_overrides_registered(self):
        @workflow("test")
        def registered_fn(e):
            return "registered"

        def passed_fn(e):
            return "passed"

        result = merge_workflows({"test": passed_fn})

        # Passed workflow should override registered
        assert result["test"] == passed_fn

    def test_merge_with_workflow_wrapper(self):
        @workflow("registered")
        def registered_fn(e):
            pass

        passed_wf = Workflow(
            fn=lambda e: None,
            reads=["entity.a"],
            writes=["entity.b"],
        )

        result = merge_workflows({"passed": passed_wf})

        assert "registered" in result
        assert "passed" in result
        assert result["passed"].reads == ["entity.a"]

