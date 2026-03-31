from rulang import RuleEngine
from rulang.workflows import Workflow


class TestRuntimeCompat:
    def test_rebuilds_dependency_order_when_workflow_metadata_is_supplied_after_inspection(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.ready == true => ret entity.value",
            "true => workflow('mark_ready')",
        ])

        assert engine.get_execution_order() == [0, 1]

        entity = {"ready": False, "value": 7}
        result = engine.evaluate(
            entity,
            workflows={
                "mark_ready": Workflow(
                    fn=lambda current: current.__setitem__("ready", True),
                    writes=["entity.ready"],
                )
            },
        )

        assert result == 7
        assert entity == {"ready": True, "value": 7}
        assert engine.get_execution_order() == [0, 1]
