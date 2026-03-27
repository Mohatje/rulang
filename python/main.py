"""
Demo script for the Rulang DSL.
"""

from rulang import RuleEngine, Workflow


def main():
    print("=== Rulang Demo ===\n")

    # Create an engine in all_match mode
    engine = RuleEngine(mode="all_match")

    # Add some business rules
    engine.add_rules([
        # Rule 1: Check if user is an adult
        "entity.age >= 18 => entity.is_adult = true",
        # Rule 2: Adults get a discount (depends on Rule 1's write)
        "entity.is_adult == true => entity.discount += 0.1",
        # Rule 3: VIP users get extra discount
        "entity.vip == true => entity.discount += 0.15",
        # Rule 4: Calculate final price
        "entity.discount > 0 => entity.final_price = entity.price * (1 - entity.discount)",
    ])

    # Show dependency analysis
    print("Rule Analysis:")
    for i in range(len(engine)):
        analysis = engine.get_rule_analysis(i)
        print(f"  Rule {i}: {analysis['rule']}")
        print(f"    Reads: {analysis['reads']}")
        print(f"    Writes: {analysis['writes']}")
    print()

    # Show execution order (respects dependencies)
    print(f"Execution Order: {engine.get_execution_order()}")
    print()

    # Test entity
    entity = {
        "age": 25,
        "is_adult": False,
        "vip": True,
        "price": 100.0,
        "discount": 0.0,
        "final_price": 0.0,
    }

    print(f"Before: {entity}")
    result = engine.evaluate(entity)
    print(f"After:  {entity}")
    print(f"Result: {result}")
    print()

    # Demo with workflows
    print("=== Workflow Demo ===\n")

    engine2 = RuleEngine()

    # Define a workflow with dependency declarations
    def apply_tax(e):
        e["price_with_tax"] = e["final_price"] * 1.2

    workflows = {
        "apply_tax": Workflow(
            fn=apply_tax,
            reads=["entity.final_price"],
            writes=["entity.price_with_tax"],
        )
    }

    engine2.add_rules([
        "entity.final_price > 0 => workflow('apply_tax'); ret entity.price_with_tax",
    ])

    entity2 = {"final_price": 90.0, "price_with_tax": 0.0}
    print(f"Before: {entity2}")
    result = engine2.evaluate(entity2, workflows=workflows)
    print(f"After:  {entity2}")
    print(f"Result (price with tax): {result}")


if __name__ == "__main__":
    main()
