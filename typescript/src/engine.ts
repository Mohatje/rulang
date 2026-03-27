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
  private executionOrderWorkflowKey: string | null = null;

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
    this.ensureExecutionOrder(allWorkflows);

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
    workflows: Record<string, WorkflowLike>,
    workflowKey: string,
  ): void {
    this.graph = new DependencyGraph();
    this.rules.forEach((rule) => this.graph.addRule(rule, workflows));
    this.executionOrder = this.graph.getExecutionOrder();
    this.executionOrderWorkflowKey = workflowKey;
  }

  private getWorkflowDependencyKey(workflows: Record<string, WorkflowLike>): string {
    const entries = Object.entries(workflows)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, workflowLike]) => {
        if (typeof workflowLike === "function") {
          return [name, null];
        }

        return [
          name,
          [...workflowLike.reads].sort(),
          [...workflowLike.writes].sort(),
        ];
      });

    return JSON.stringify(entries);
  }

  private ensureExecutionOrder(workflows: Record<string, WorkflowLike>): void {
    const workflowKey = this.getWorkflowDependencyKey(workflows);
    if (
      this.executionOrder === null ||
      this.executionOrderWorkflowKey !== workflowKey
    ) {
      this.buildExecutionOrder(workflows, workflowKey);
    }
  }

  public getDependencyGraph(): Record<number, Set<number>> {
    this.ensureExecutionOrder(mergeWorkflows());
    return this.graph.getGraph();
  }

  public getExecutionOrder(): number[] {
    this.ensureExecutionOrder(mergeWorkflows());
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
    this.executionOrderWorkflowKey = null;
  }

  public get size(): number {
    return this.rules.length;
  }
}
