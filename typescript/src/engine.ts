import { DependencyGraph } from "./dependencyGraph.js";
import {
  deepCopy,
  diffEntities,
  mergeIntoAggregate,
  type ActionChange,
  type ActionKind,
  type DryRunResult,
  type ExecutedAction,
  type MatchedRule,
} from "./dryRun.js";
import {
  EvaluationError,
  PathResolutionError,
  WorkflowNotFoundError,
} from "./errors.js";
import {
  ReturnValue,
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

  public dryRun(
    entity: unknown,
    options: {
      workflows?: Record<string, WorkflowLike>;
      entityName?: string;
      deepCopy?: boolean;
    } = {},
  ): DryRunResult {
    const { workflows, entityName = "entity", deepCopy: shouldCopy = true } = options;
    let current = shouldCopy ? deepCopy(entity) : entity;

    const allWorkflows = mergeWorkflows(workflows);
    this.ensureExecutionOrder(allWorkflows);

    const matchedRules: MatchedRule[] = [];
    const executedActions: ExecutedAction[] = [];
    const aggregate: Record<string, [unknown, unknown]> = {};
    let lastReturnValue: unknown = null;
    let anyExecuted = false;
    let firstMatchExecuted = false;
    let stopAll = false;
    let returned: unknown = null;

    for (const ruleIndex of this.executionOrder ?? []) {
      if (stopAll) {
        const parsed = this.rules[ruleIndex];
        matchedRules.push({
          index: ruleIndex,
          ruleText: parsed.ruleText,
          conditionResult: false,
          executed: false,
        });
        continue;
      }

      const parsed = this.rules[ruleIndex];
      const interpreter = new RuleInterpreter(current, allWorkflows, entityName);

      let conditionValue: unknown;
      try {
        conditionValue = interpreter.visitNode(parsed.tree.condition());
      } catch (error) {
        if (
          error instanceof EvaluationError ||
          error instanceof PathResolutionError ||
          error instanceof WorkflowNotFoundError
        ) {
          throw error;
        }
        throw new EvaluationError(
          parsed.ruleText,
          error instanceof Error ? error.message : String(error),
        );
      }

      const matched = this.pythonTruthy(conditionValue);
      let executeThis = false;
      if (matched) {
        if (this.mode === "all_match") {
          executeThis = true;
        } else if (!firstMatchExecuted) {
          executeThis = true;
          firstMatchExecuted = true;
        }
      }

      if (executeThis) {
        anyExecuted = true;
        const { returnValue: rv, stopped } = this.executeActionsTraced(
          parsed,
          ruleIndex,
          interpreter,
          current,
          executedActions,
          aggregate,
        );
        if (rv !== NO_RETURN) {
          lastReturnValue = rv;
          if (this.mode === "first_match") stopAll = true;
        } else if (lastReturnValue === null) {
          lastReturnValue = true;
        }
        if (stopped) {
          stopAll = true;
        }
      }

      matchedRules.push({
        index: ruleIndex,
        ruleText: parsed.ruleText,
        conditionResult: matched,
        executed: executeThis,
      });

      if (executeThis && this.mode === "first_match") {
        stopAll = true;
      }
    }

    if (anyExecuted) {
      returned = lastReturnValue;
    }

    return {
      matchedRules,
      executedActions,
      diff: aggregate,
      finalEntity: current,
      returned,
      anyMatched: matchedRules.some((m) => m.executed),
    };
  }

  private executeActionsTraced(
    parsed: ParsedRule,
    ruleIndex: number,
    interpreter: RuleInterpreter,
    entity: unknown,
    executed: ExecutedAction[],
    aggregate: Record<string, [unknown, unknown]>,
  ): { returnValue: unknown; stopped: boolean } {
    const actionsCtx = parsed.tree.actions();
    const actionList: unknown[] = (actionsCtx as unknown as { action_list(): unknown[] }).action_list();
    for (const actionCtx of actionList) {
      const beforeSnap = deepCopy(entity);
      try {
        interpreter.visitNode(actionCtx as Parameters<typeof interpreter.visitNode>[0]);
      } catch (error) {
        if (error instanceof ReturnValue) {
          const changesMap = diffEntities(beforeSnap, entity);
          for (const [path, [b, a]] of Object.entries(changesMap)) {
            mergeIntoAggregate(aggregate, path, b, a);
          }
          executed.push({
            ruleIndex,
            actionKind: "return",
            changes: toChanges(changesMap),
            returned: error.value,
          });
          return { returnValue: error.value, stopped: false };
        }
        throw error;
      }

      const kind = actionKind(actionCtx);
      const changesMap = diffEntities(beforeSnap, entity);
      for (const [path, [b, a]] of Object.entries(changesMap)) {
        mergeIntoAggregate(aggregate, path, b, a);
      }
      executed.push({
        ruleIndex,
        actionKind: kind,
        changes: toChanges(changesMap),
      });
    }
    return { returnValue: NO_RETURN, stopped: false };
  }

  private pythonTruthy(value: unknown): boolean {
    if (value === null || value === undefined) return false;
    if (typeof value === "boolean") return value;
    if (typeof value === "number") return value !== 0 && !Number.isNaN(value);
    if (typeof value === "string") return value.length > 0;
    if (Array.isArray(value)) return value.length > 0;
    return true;
  }
}

const NO_RETURN = Symbol("no-return");

function toChanges(map: Record<string, [unknown, unknown]>): ActionChange[] {
  return Object.entries(map)
    .sort(([l], [r]) => l.localeCompare(r))
    .map(([path, [before, after]]) => ({ path, before, after }));
}

function actionKind(ctx: unknown): ActionKind {
  const c = ctx as {
    returnStmt(): unknown;
    assignment(): null | { assignOp(): { ASSIGN(): unknown } };
    workflowCall(): unknown;
  };
  if (c.returnStmt()) return "return";
  const assign = c.assignment();
  if (assign) {
    if (assign.assignOp().ASSIGN()) return "set";
    return "compound";
  }
  if (c.workflowCall()) return "workflow";
  return "set";
}
