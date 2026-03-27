import { readFileSync } from "node:fs";
import { readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, test } from "vitest";
import { RuleEngine, RuleSyntaxError, Workflow, parseRule } from "../src/index.js";

type WorkflowExpr =
  | { type: "literal"; value: unknown }
  | { type: "entity_path"; path: string }
  | { type: "arg"; index: number }
  | { type: "binary"; op: "add" | "sub" | "mul" | "div" | "mod"; left: WorkflowExpr; right: WorkflowExpr }
  | { type: "call"; fn: "upper"; arg: WorkflowExpr };

type WorkflowStep =
  | { type: "set"; path: string; value: WorkflowExpr }
  | { type: "return"; value: WorkflowExpr };

type WorkflowSpec = {
  name: string;
  reads?: string[];
  writes?: string[];
  steps: WorkflowStep[];
};

type PortableCase =
  | {
      id: string;
      kind: "evaluate";
      mode: "first_match" | "all_match";
      rules: string[];
      input: Record<string, unknown>;
      expected_result: unknown;
      expected_entity?: Record<string, unknown>;
      workflows?: WorkflowSpec[];
    }
  | {
      id: string;
      kind: "parse";
      rule: string;
      entity_name?: string | null;
      expected: {
        reads: string[];
        writes: string[];
        workflow_calls: string[];
      };
    }
  | {
      id: string;
      kind: "parse_error";
      rule: string;
      entity_name?: string | null;
      expected_error: string;
    };

const casesPath = resolve(process.cwd(), "..", "spec", "generated", "python-portable-cases.json");
const portableCasesDir = resolve(process.cwd(), "..", "spec", "portable");
const cases = [
  ...(JSON.parse(readFileSync(casesPath, "utf8")) as PortableCase[]),
  ...readdirSync(portableCasesDir)
    .filter((file) => file.endsWith(".json"))
    .sort()
    .flatMap((file) => JSON.parse(readFileSync(join(portableCasesDir, file), "utf8")) as PortableCase[]),
];

function getPath(entity: Record<string, unknown>, path: string): unknown {
  let current: unknown = entity;
  for (const segment of path.split(".")) {
    current = (current as Record<string, unknown>)[segment];
  }
  return current;
}

function setPath(entity: Record<string, unknown>, path: string, value: unknown): void {
  const parts = path.split(".");
  let current: Record<string, unknown> = entity;
  for (const segment of parts.slice(0, -1)) {
    current = current[segment] as Record<string, unknown>;
  }
  current[parts.at(-1)!] = value;
}

function evalWorkflowExpr(expr: WorkflowExpr, entity: Record<string, unknown>, args: unknown[]): unknown {
  if (expr.type === "literal") return expr.value;
  if (expr.type === "entity_path") return getPath(entity, expr.path);
  if (expr.type === "arg") return args[expr.index];
  if (expr.type === "binary") {
    const left = evalWorkflowExpr(expr.left, entity, args) as number | string;
    const right = evalWorkflowExpr(expr.right, entity, args) as number | string;
    if (expr.op === "add") return (left as never) + (right as never);
    if (expr.op === "sub") return (left as never) - (right as never);
    if (expr.op === "mul") return (left as never) * (right as never);
    if (expr.op === "div") return (left as never) / (right as never);
    return (left as never) % (right as never);
  }
  if (expr.fn === "upper") {
    return String(evalWorkflowExpr(expr.arg, entity, args)).toUpperCase();
  }
  throw new Error(`Unsupported workflow expression: ${JSON.stringify(expr)}`);
}

function buildWorkflows(parityCase: PortableCase): Record<string, unknown> | undefined {
  if (parityCase.kind !== "evaluate" || !parityCase.workflows?.length) {
    return undefined;
  }

  return Object.fromEntries(
    parityCase.workflows.map((spec) => {
      const fn = (entity: unknown, ...args: unknown[]) => {
        for (const step of spec.steps) {
          if (step.type === "set") {
            setPath(entity as Record<string, unknown>, step.path, evalWorkflowExpr(step.value, entity as Record<string, unknown>, args));
            continue;
          }
          return evalWorkflowExpr(step.value, entity as Record<string, unknown>, args);
        }
        return null;
      };

      const workflow =
        spec.reads || spec.writes
          ? new Workflow({ fn, reads: spec.reads ?? [], writes: spec.writes ?? [] })
          : fn;
      return [spec.name, workflow];
    }),
  );
}

describe("portable python parity corpus", () => {
  for (const parityCase of cases) {
    test(parityCase.id, () => {
      if (parityCase.kind === "evaluate") {
        const engine = new RuleEngine(parityCase.mode);
        engine.addRules(parityCase.rules);
        const entity = structuredClone(parityCase.input);
        const result = engine.evaluate(entity, buildWorkflows(parityCase));
        expect(result).toEqual(parityCase.expected_result);
        if (parityCase.expected_entity) {
          expect(entity).toEqual(parityCase.expected_entity);
        }
        return;
      }

      if (parityCase.kind === "parse") {
        const parsed = parseRule(parityCase.rule, parityCase.entity_name ?? "entity");
        expect([...parsed.reads].sort()).toEqual(parityCase.expected.reads);
        expect([...parsed.writes].sort()).toEqual(parityCase.expected.writes);
        expect([...parsed.workflowCalls].sort()).toEqual(parityCase.expected.workflow_calls);
        return;
      }

      expect(() => parseRule(parityCase.rule, parityCase.entity_name ?? "entity")).toThrowError(RuleSyntaxError);
    });
  }
});
