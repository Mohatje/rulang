"""End-to-end integration tests for the new API surface (proposals 1-5, 7, 8).

Covers the real-world flow of:
  1. build rule programmatically with builders
  2. format to canonical text
  3. parse back
  4. validate against a custom Resolver
  5. detect conflicts across rule sets
  6. dry-run against entities
"""

from __future__ import annotations

from rulang import (
    BaseResolver,
    PathInfo,
    RuleEngine,
    detect_conflicts,
    format,
    parse,
    validate,
)
from rulang.ast import Path
from rulang.builders import (
    and_,
    compound,
    eq,
    gt,
    gte,
    lit,
    pathref,
    ret,
    rule,
    set_,
    workflow_call,
)


def test_build_format_reparse_validate_dry_run_end_to_end():
    r = rule(
        condition=and_(gte(pathref("entity.age"), 18), eq(pathref("entity.status"), lit("active"))),
        actions=[set_("entity.adult", True)],
    )

    text = format(r)
    assert text == "entity.age >= 18 and entity.status == 'active' => entity.adult = true"

    reparsed = parse(text)
    assert reparsed.reads == r.reads
    assert reparsed.writes == r.writes

    assert validate(reparsed, BaseResolver()) == []

    engine = RuleEngine()
    engine.add_rules(text)
    result = engine.dry_run({"age": 25, "status": "active", "adult": False})
    assert result.final_entity["adult"] is True
    assert result.diff == {"adult": (False, True)}


def test_schema_aware_validation_with_custom_resolver():
    class SchemaResolver(BaseResolver):
        KNOWN = {"entity.age", "entity.status", "entity.adult"}
        WRITABLE = {"entity.adult"}

        def check_path(self, path: Path) -> PathInfo:
            p = path.to_string(normalize_entity="entity", include_indices=False)
            if p not in self.KNOWN:
                return PathInfo(exists=False)
            return PathInfo(exists=True, writable=p in self.WRITABLE)

    diagnostics = validate(
        "entity.age >= 18 and entity.stauts == 'active' => entity.adult = true",
        SchemaResolver(),
    )
    assert any(d.code == "rulang.unknown_path" for d in diagnostics)

    diagnostics = validate(
        "entity.age >= 18 => entity.status = 'active'",
        SchemaResolver(),
    )
    assert any(d.code == "rulang.path_not_writable" for d in diagnostics)


def test_conflict_detection_across_builder_built_rules():
    a = rule(eq(pathref("entity.x"), 1), [set_("entity.y", lit("a"))])
    b = rule(eq(pathref("entity.x"), 1), [set_("entity.y", lit("b"))])
    conflicts = detect_conflicts([a, b])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "contradiction"


def test_round_trip_preserves_semantic_equivalence():
    built = rule(
        condition=gt(pathref("entity.score"), 100),
        actions=[compound("entity.bonus", "+=", 10), ret(lit("rewarded"))],
    )

    engine1 = RuleEngine()
    engine1.add_rules(format(built))
    entity1 = {"score": 150, "bonus": 0}
    result1 = engine1.evaluate(entity1)

    engine2 = RuleEngine()
    engine2.add_rules(format(parse(format(built))))
    entity2 = {"score": 150, "bonus": 0}
    result2 = engine2.evaluate(entity2)

    assert result1 == result2 == "rewarded"
    assert entity1 == entity2 == {"score": 150, "bonus": 10}


def test_conflict_detection_and_dry_run_cooperate():
    rules_text = [
        "entity.x == 1 => entity.y = 'a'",
        "entity.x == 1 => entity.y = 'b'",
    ]

    conflicts = detect_conflicts(rules_text, mode="all_match")
    assert any(c.kind == "contradiction" for c in conflicts)

    engine = RuleEngine("all_match")
    engine.add_rules(rules_text)
    result = engine.dry_run({"x": 1, "y": ""})
    assert result.final_entity["y"] in {"a", "b"}


def test_validate_with_severity_overrides():
    class UnknownPath(BaseResolver):
        def check_path(self, path: Path) -> PathInfo:
            return PathInfo(exists=False)

    result = validate(
        "entity.missing == 1 => entity.unknown = 2",
        UnknownPath(),
        severity_overrides={"rulang.unknown_path": "warning"},
    )
    assert len(result) >= 2
    for d in result:
        if d.code == "rulang.unknown_path":
            assert d.severity == "warning"


def test_builders_and_workflow_call_integration():
    r = rule(
        condition=eq(pathref("entity.trigger"), True),
        actions=[workflow_call("notify", pathref("entity.email"))],
    )
    assert "notify" in r.workflow_calls

    text = format(r)
    engine = RuleEngine()
    engine.add_rules(text)

    calls: list[str] = []

    def notify(_entity, email):
        calls.append(email)

    result = engine.dry_run(
        {"trigger": True, "email": "a@b.com"},
        workflows={"notify": notify},
    )
    assert calls == ["a@b.com"]
    assert result.returned is True


def test_validation_and_conflict_detection_compose():
    class Schema(BaseResolver):
        def check_path(self, path: Path) -> PathInfo:
            p = path.to_string(normalize_entity="entity", include_indices=False)
            return PathInfo(exists=p == "entity.x" or p == "entity.y")

    rules = [
        "entity.x == 1 => entity.y = 'a'",
        "entity.x == 1 => entity.y = 'b'",
        "entity.unknown == 1 => entity.y = 'c'",
    ]

    conflicts = detect_conflicts(rules)
    assert any(c.kind == "contradiction" for c in conflicts)

    diagnostics = validate(rules[2], Schema())
    assert any(d.code == "rulang.unknown_path" for d in diagnostics)
