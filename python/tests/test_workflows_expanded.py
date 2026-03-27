"""Comprehensive expanded tests for workflows."""

import pytest

from rulang.workflows import (
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


class TestWorkflowClassExpanded:
    """Expanded tests for Workflow wrapper class."""

    def test_creation_with_all_parameters(self):
        def my_fn(entity):
            return entity["value"] * 2
        
        wf = Workflow(
            fn=my_fn,
            reads=["entity.value"],
            writes=["entity.result"]
        )
        
        assert wf.fn == my_fn
        assert wf.reads == ["entity.value"]
        assert wf.writes == ["entity.result"]

    def test_creation_with_defaults(self):
        def my_fn(entity):
            pass
        
        wf = Workflow(fn=my_fn)
        
        assert wf.fn == my_fn
        assert wf.reads == []
        assert wf.writes == []

    def test_creation_with_empty_lists(self):
        def my_fn(entity):
            pass
        
        wf = Workflow(fn=my_fn, reads=[], writes=[])
        
        assert wf.reads == []
        assert wf.writes == []

    def test_callable_behavior(self):
        def double(entity):
            return entity["value"] * 2
        
        wf = Workflow(fn=double, reads=["entity.value"], writes=[])
        
        result = wf({"value": 10})
        assert result == 20

    def test_callable_with_multiple_args(self):
        def multiply(entity, a, b):
            return a * b
        
        wf = Workflow(fn=multiply, reads=[], writes=[])
        
        result = wf({}, 5, 3)
        assert result == 15

    def test_callable_preserves_function(self):
        def original_fn(entity):
            return "original"
        
        wf = Workflow(fn=original_fn)
        
        assert wf.fn == original_fn
        assert wf({}) == "original"


class TestWorkflowDecoratorExpanded:
    """Expanded tests for @workflow decorator."""

    def test_basic_registration(self):
        @workflow("my_workflow")
        def my_fn(entity):
            pass
        
        registry = get_registered_workflows()
        assert "my_workflow" in registry
        assert registry["my_workflow"].fn == my_fn

    def test_registration_with_reads_only(self):
        @workflow("read_only", reads=["entity.input"])
        def read_fn(entity):
            return entity["input"]
        
        registry = get_registered_workflows()
        wf = registry["read_only"]
        
        assert wf.reads == ["entity.input"]
        assert wf.writes == []

    def test_registration_with_writes_only(self):
        @workflow("write_only", writes=["entity.output"])
        def write_fn(entity):
            entity["output"] = 10
        
        registry = get_registered_workflows()
        wf = registry["write_only"]
        
        assert wf.reads == []
        assert wf.writes == ["entity.output"]

    def test_registration_with_both(self):
        @workflow("both", reads=["entity.input"], writes=["entity.output"])
        def both_fn(entity):
            entity["output"] = entity["input"] * 2
        
        registry = get_registered_workflows()
        wf = registry["both"]
        
        assert wf.reads == ["entity.input"]
        assert wf.writes == ["entity.output"]

    def test_multiple_registrations(self):
        @workflow("first")
        def first_fn(e):
            pass
        
        @workflow("second")
        def second_fn(e):
            pass
        
        @workflow("third")
        def third_fn(e):
            pass
        
        registry = get_registered_workflows()
        
        assert "first" in registry
        assert "second" in registry
        assert "third" in registry
        assert len(registry) == 3

    def test_duplicate_name_override(self):
        @workflow("test")
        def first_fn(e):
            return "first"
        
        @workflow("test")
        def second_fn(e):
            return "second"
        
        registry = get_registered_workflows()
        
        # Second registration should override first
        assert registry["test"].fn == second_fn

    def test_decorator_preserves_function(self):
        @workflow("test")
        def my_fn(entity):
            return "result"
        
        # Original function should still work
        assert my_fn({}) == "result"

    def test_decorator_with_dependencies(self):
        @workflow("process", reads=["entity.input", "entity.config"], writes=["entity.output"])
        def process_fn(entity):
            entity["output"] = entity["input"] * entity["config"]
        
        registry = get_registered_workflows()
        wf = registry["process"]
        
        assert len(wf.reads) == 2
        assert "entity.input" in wf.reads
        assert "entity.config" in wf.reads
        assert wf.writes == ["entity.output"]


class TestWorkflowRegistryExpanded:
    """Expanded tests for workflow registry."""

    def test_add_workflow(self):
        @workflow("test")
        def test_fn(e):
            pass
        
        registry = get_registered_workflows()
        assert "test" in registry

    def test_override_workflow(self):
        @workflow("test")
        def first_fn(e):
            return 1
        
        @workflow("test")
        def second_fn(e):
            return 2
        
        registry = get_registered_workflows()
        assert registry["test"].fn == second_fn

    def test_clear_registry(self):
        @workflow("test1")
        def test1_fn(e):
            pass
        
        @workflow("test2")
        def test2_fn(e):
            pass
        
        assert len(get_registered_workflows()) == 2
        
        clear_workflow_registry()
        
        assert len(get_registered_workflows()) == 0

    def test_get_registered_workflows_returns_copy(self):
        @workflow("test")
        def test_fn(e):
            pass
        
        registry1 = get_registered_workflows()
        registry2 = get_registered_workflows()
        
        # Should be different objects
        assert registry1 is not registry2
        # But same content
        assert registry1 == registry2
        
        # Modifying one shouldn't affect the other
        registry1["new"] = Workflow(fn=lambda e: None)
        assert "new" not in get_registered_workflows()

    def test_empty_registry(self):
        clear_workflow_registry()
        registry = get_registered_workflows()
        assert len(registry) == 0

    def test_large_registry(self):
        for i in range(20):
            @workflow(f"workflow_{i}")
            def workflow_fn(e):
                pass
        
        registry = get_registered_workflows()
        assert len(registry) == 20


class TestMergeWorkflowsExpanded:
    """Expanded tests for workflow merging."""

    def test_merge_none_with_registered(self):
        @workflow("registered")
        def registered_fn(e):
            e["registered"] = True
        
        result = merge_workflows(None)
        
        assert "registered" in result
        assert result["registered"].fn == registered_fn

    def test_merge_empty_dict_with_registered(self):
        @workflow("registered")
        def registered_fn(e):
            pass
        
        result = merge_workflows({})
        
        assert "registered" in result

    def test_merge_passed_with_registered(self):
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
        
        # Passed should override
        assert result["test"] == passed_fn

    def test_merge_with_workflow_wrapper(self):
        @workflow("registered")
        def registered_fn(e):
            pass
        
        passed_wf = Workflow(
            fn=lambda e: None,
            reads=["entity.a"],
            writes=["entity.b"]
        )
        
        result = merge_workflows({"passed": passed_wf})
        
        assert "registered" in result
        assert "passed" in result
        assert isinstance(result["passed"], Workflow)
        assert result["passed"].reads == ["entity.a"]

    def test_merge_mixed_types(self):
        @workflow("registered")
        def registered_fn(e):
            pass
        
        def plain_fn(e):
            pass
        
        wrapped_fn = Workflow(fn=lambda e: None, reads=["entity.a"], writes=[])
        
        result = merge_workflows({
            "plain": plain_fn,
            "wrapped": wrapped_fn,
        })
        
        assert "registered" in result
        assert "plain" in result
        assert "wrapped" in result
        assert result["plain"] == plain_fn
        assert isinstance(result["wrapped"], Workflow)

    def test_merge_preserves_workflow_attributes(self):
        passed_wf = Workflow(
            fn=lambda e: None,
            reads=["entity.input"],
            writes=["entity.output"]
        )
        
        result = merge_workflows({"test": passed_wf})
        
        assert isinstance(result["test"], Workflow)
        assert result["test"].reads == ["entity.input"]
        assert result["test"].writes == ["entity.output"]

    def test_merge_multiple_passed(self):
        @workflow("registered")
        def registered_fn(e):
            pass
        
        workflows = {
            "passed1": lambda e: None,
            "passed2": Workflow(fn=lambda e: None, reads=[], writes=[]),
            "passed3": lambda e: None,
        }
        
        result = merge_workflows(workflows)
        
        assert "registered" in result
        assert "passed1" in result
        assert "passed2" in result
        assert "passed3" in result

