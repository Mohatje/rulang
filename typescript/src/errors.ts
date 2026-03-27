export class RuleInterpreterError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RuleInterpreterError";
  }
}

export class PathResolutionError extends RuleInterpreterError {
  public readonly path: string;
  public readonly entityType: string;
  public readonly reason: string;

  constructor(path: string, entityType: string, reason = "") {
    const suffix = reason ? `: ${reason}` : "";
    super(`Cannot resolve path '${path}' on entity of type '${entityType}'${suffix}`);
    this.name = "PathResolutionError";
    this.path = path;
    this.entityType = entityType;
    this.reason = reason;
  }
}

export class RuleSyntaxError extends RuleInterpreterError {
  public readonly rule: string;
  public readonly line?: number;
  public readonly column?: number;

  constructor(rule: string, message: string, line?: number, column?: number) {
    const location =
      line === undefined
        ? ""
        : column === undefined
          ? ` at line ${line}`
          : ` at line ${line}, column ${column}`;
    super(`Syntax error${location}: ${message}\nRule: ${rule}`);
    this.name = "RuleSyntaxError";
    this.rule = rule;
    this.line = line;
    this.column = column;
  }
}

export class CyclicDependencyWarning extends Error {
  public readonly cycle: number[];

  constructor(cycle: number[]) {
    super(`Cyclic dependency detected in rules: ${cycle.join(" -> ")}`);
    this.name = "CyclicDependencyWarning";
    this.cycle = cycle;
  }
}

export class WorkflowNotFoundError extends RuleInterpreterError {
  public readonly workflow: string;

  constructor(name: string) {
    super(`Workflow '${name}' not found in registered workflows`);
    this.name = "WorkflowNotFoundError";
    this.workflow = name;
  }
}

export class EvaluationError extends RuleInterpreterError {
  public readonly rule: string;

  constructor(rule: string, message: string) {
    super(`Error evaluating rule: ${message}\nRule: ${rule}`);
    this.name = "EvaluationError";
    this.rule = rule;
  }
}
