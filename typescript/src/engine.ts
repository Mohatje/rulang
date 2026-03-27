import { DependencyGraph } from "./dependencyGraph.js";
import {
  EvaluationError,
  PathResolutionError,
  WorkflowNotFoundError,
} from "./errors.js";
import {
  RuleInterpreter,
  parseRule,
  type ParsedRule,
} from "./visitor.js";
import {
  mergeWorkflows,
  workflow,
  type WorkflowLike,
} from "./workflows.js";

export type EvaluationMode = "first_match" | "all_match";

export class RuleEngine {
  public static workflow = workflow;
  private readonly rules: ParsedRule[] = [];
  private graph = new DependencyGraph();
  private executionOrder: number[] | null = null;

  public constructor(private readonly mode: EvaluationMode = "first_match") {}

  public addRules(rules: string | string[]): void {
    const ruleList = typeof rules === "string" ? [rules] : rules;
    ruleList.forEach((ruleText) => {
      this.rules.push(parseRule(ruleText));
    });
    this.executionOrder = null;
  }

  public evaluate(
    entity: unknown,
    workflows?: Record<string, WorkflowLike>,
    entityName = "entity",
  ): unknown {
    const allWorkflows = mergeWorkflows(workflows);
    if (this.executionOrder === null) {
      this.buildExecutionOrder(allWorkflows);
    }

    let anyMatched = false;
    let lastReturnValue: unknown = null;

    for (const ruleIndex of this.executionOrder ?? []) {
      const rule = this.rules[ruleIndex];

      try {
        const interpreter = new RuleInterpreter(entity, allWorkflows, entityName);
        const [matched, returnValue] = interpreter.execute(rule.tree);

        if (matched) {
          anyMatched = true;
          lastReturnValue = returnValue;
          if (this.mode === "first_match") {
            return returnValue;
          }
        }
      } catch (error) {
        if (
          error instanceof EvaluationError ||
          error instanceof PathResolutionError ||
          error instanceof WorkflowNotFoundError
        ) {
          throw error;
        }

        throw new EvaluationError(
          rule.ruleText,
          error instanceof Error ? error.message : String(error),
        );
      }
    }

    return anyMatched ? lastReturnValue : null;
  }

  private buildExecutionOrder(
    workflows?: Record<string, WorkflowLike>,
  ): void {
    this.graph = new DependencyGraph();
    this.rules.forEach((rule) => this.graph.addRule(rule, workflows));
    this.executionOrder = this.graph.getExecutionOrder();
  }

  public getDependencyGraph(): Record<number, Set<number>> {
    if (this.executionOrder === null) {
      this.buildExecutionOrder();
    }
    return this.graph.getGraph();
  }

  public getExecutionOrder(): number[] {
    if (this.executionOrder === null) {
      this.buildExecutionOrder();
    }
    return [...(this.executionOrder ?? [])];
  }

  public getRules(): string[] {
    return this.rules.map((rule) => rule.ruleText);
  }

  public getRuleAnalysis(index: number): {
    rule: string;
    reads: Set<string>;
    writes: Set<string>;
    workflowCalls: Set<string>;
  } {
    if (index < 0 || index >= this.rules.length) {
      throw new RangeError(`Rule index ${index} out of range`);
    }

    const rule = this.rules[index];
    return {
      rule: rule.ruleText,
      reads: new Set(rule.reads),
      writes: new Set(rule.writes),
      workflowCalls: new Set(rule.workflowCalls),
    };
  }

  public clear(): void {
    this.rules.splice(0, this.rules.length);
    this.graph = new DependencyGraph();
    this.executionOrder = null;
  }

  public get size(): number {
    return this.rules.length;
  }
}
