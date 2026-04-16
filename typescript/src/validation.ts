/**
 * Generic validation framework (proposal #4).
 *
 * Mirrors `rulang/validation.py`. Rulang walks the AST; the user's
 * Resolver answers domain questions; diagnostics accumulate. validate()
 * never throws — parse errors become `rulang.syntax_error` diagnostics.
 */

import {
  parse,
  pathToString,
  type ComparisonOp,
  type Condition,
  type Expr,
  type Literal,
  type Path,
  type Rule,
  type Span,
  type Action,
} from "./ast.js";
import { RuleSyntaxError } from "./errors.js";

export type Severity = "error" | "warning" | "info";

// --- Sentinels ----------------------------------------------------------

class Sentinel {
  constructor(public readonly name: string) {}
  toString() { return this.name; }
}

export const UNKNOWN = new Sentinel("UNKNOWN");
export const OK = new Sentinel("OK");

function isSentinel(v: unknown): v is Sentinel {
  return v === UNKNOWN || v === OK;
}

// --- Types --------------------------------------------------------------

export interface PathInfo {
  readonly exists?: boolean;
  readonly writable?: boolean;
  readonly type?: string;
}

export interface Diagnostic {
  readonly code: string;
  readonly message: string;
  readonly severity: Severity;
  readonly span?: Span;
  readonly related?: readonly Diagnostic[];
}

export interface Resolver {
  checkPath(path: Path): PathInfo | Sentinel;
  checkAssignment(path: Path, value: Expr): Sentinel | Diagnostic[];
  checkComparison(left: Expr, op: ComparisonOp, right: Expr): Sentinel | Diagnostic[];
  checkWorkflowCall(name: string, args: readonly Expr[]): Sentinel | Diagnostic[];
}

export class BaseResolver implements Resolver {
  checkPath(_path: Path): PathInfo | Sentinel {
    return UNKNOWN;
  }
  checkAssignment(_path: Path, _value: Expr): Sentinel | Diagnostic[] {
    return OK;
  }
  checkComparison(_left: Expr, _op: ComparisonOp, _right: Expr): Sentinel | Diagnostic[] {
    return OK;
  }
  checkWorkflowCall(_name: string, _args: readonly Expr[]): Sentinel | Diagnostic[] {
    return OK;
  }
}

// --- Rulang-owned codes -------------------------------------------------

export const DIAGNOSTIC_CODES = [
  "rulang.syntax_error",
  "rulang.unknown_path",
  "rulang.path_not_writable",
  "rulang.type_mismatch",
  "rulang.unknown_workflow",
  "rulang.workflow_arg_mismatch",
  "rulang.invalid_literal",
] as const;

const DEFAULT_SEVERITIES: Record<string, Severity> = {
  "rulang.syntax_error": "error",
  "rulang.unknown_path": "error",
  "rulang.path_not_writable": "error",
  "rulang.type_mismatch": "error",
  "rulang.unknown_workflow": "error",
  "rulang.workflow_arg_mismatch": "error",
  "rulang.invalid_literal": "error",
};

// --- validate() --------------------------------------------------------

export function validate(
  ruleOrText: string | Rule,
  resolver: Resolver,
  options: {
    severityOverrides?: Record<string, Severity>;
    entityName?: string;
  } = {},
): Diagnostic[] {
  const overrides = options.severityOverrides ?? {};
  const diagnostics: Diagnostic[] = [];

  let rule: Rule;
  if (typeof ruleOrText === "string") {
    try {
      rule = parse(ruleOrText, options.entityName ?? "entity");
    } catch (error) {
      if (error instanceof RuleSyntaxError) {
        add(
          diagnostics,
          {
            code: "rulang.syntax_error",
            message: error.message,
            severity: "error",
            span:
              error.line !== undefined && error.column !== undefined
                ? {
                    start: 0,
                    end: ruleOrText.length,
                    line: error.line,
                    column: error.column + 1,
                  }
                : undefined,
          },
          overrides,
        );
        return diagnostics;
      }
      throw error;
    }
  } else {
    rule = ruleOrText;
  }

  validateCondition(rule.condition, resolver, diagnostics, overrides);
  for (const action of rule.actions) {
    validateAction(action, resolver, diagnostics, overrides);
  }

  return diagnostics;
}

// --- Traversal ---------------------------------------------------------

function validateCondition(
  cond: Condition,
  resolver: Resolver,
  diagnostics: Diagnostic[],
  overrides: Record<string, Severity>,
): void {
  switch (cond.type) {
    case "and":
    case "or":
      validateCondition(cond.left, resolver, diagnostics, overrides);
      validateCondition(cond.right, resolver, diagnostics, overrides);
      return;
    case "not":
      validateCondition(cond.inner, resolver, diagnostics, overrides);
      return;
    case "comparison":
      walkExprForPaths(cond.left, resolver, diagnostics, overrides);
      walkExprForPaths(cond.right, resolver, diagnostics, overrides);
      handleHook(
        resolver.checkComparison(cond.left, cond.op, cond.right),
        diagnostics,
        overrides,
      );
      return;
    case "existence":
      walkExprForPaths(cond.expr, resolver, diagnostics, overrides);
      return;
  }
}

function validateAction(
  action: Action,
  resolver: Resolver,
  diagnostics: Diagnostic[],
  overrides: Record<string, Severity>,
): void {
  if (action.type === "set" || action.type === "compound") {
    const info = resolver.checkPath(action.path);
    if (!isSentinel(info)) {
      if (info.exists === false) {
        add(
          diagnostics,
          {
            code: "rulang.unknown_path",
            message: `Unknown path: ${pathToString(action.path, { normalizeEntity: null })}`,
            severity: "error",
            span: action.path.span,
          },
          overrides,
        );
      } else if (info.writable === false) {
        add(
          diagnostics,
          {
            code: "rulang.path_not_writable",
            message: `Path is not writable: ${pathToString(action.path, { normalizeEntity: null })}`,
            severity: "error",
            span: action.path.span,
          },
          overrides,
        );
      }
    }
    walkPathIndices(action.path, resolver, diagnostics, overrides);
    walkExprForPaths(action.value, resolver, diagnostics, overrides);
    handleHook(resolver.checkAssignment(action.path, action.value), diagnostics, overrides);
    return;
  }
  if (action.type === "workflowCallAction") {
    handleHook(
      resolver.checkWorkflowCall(action.name, action.args),
      diagnostics,
      overrides,
    );
    for (const a of action.args) walkExprForPaths(a, resolver, diagnostics, overrides);
    return;
  }
  if (action.type === "return") {
    walkExprForPaths(action.value, resolver, diagnostics, overrides);
    return;
  }
}

function walkExprForPaths(
  expr: Expr,
  resolver: Resolver,
  diagnostics: Diagnostic[],
  overrides: Record<string, Severity>,
): void {
  switch (expr.type) {
    case "pathRef": {
      const info = resolver.checkPath(expr.path);
      if (!isSentinel(info) && info.exists === false) {
        add(
          diagnostics,
          {
            code: "rulang.unknown_path",
            message: `Unknown path: ${pathToString(expr.path, { normalizeEntity: null })}`,
            severity: "error",
            span: expr.path.span,
          },
          overrides,
        );
      }
      walkPathIndices(expr.path, resolver, diagnostics, overrides);
      return;
    }
    case "functionCall":
      for (const a of expr.args) walkExprForPaths(a, resolver, diagnostics, overrides);
      return;
    case "binary":
    case "nullCoalesce":
      walkExprForPaths(expr.left, resolver, diagnostics, overrides);
      walkExprForPaths(expr.right, resolver, diagnostics, overrides);
      return;
    case "unary":
      walkExprForPaths(expr.expr, resolver, diagnostics, overrides);
      return;
    case "workflowCallExpr":
      handleHook(resolver.checkWorkflowCall(expr.name, expr.args), diagnostics, overrides);
      for (const a of expr.args) walkExprForPaths(a, resolver, diagnostics, overrides);
      return;
    case "literal":
      if (expr.literalType === "list") {
        for (const item of expr.value as Expr[]) walkExprForPaths(item, resolver, diagnostics, overrides);
      }
      return;
  }
}

function walkPathIndices(
  path: Path,
  resolver: Resolver,
  diagnostics: Diagnostic[],
  overrides: Record<string, Severity>,
): void {
  for (const seg of path.segments) {
    if (seg.kind === "index") {
      walkExprForPaths(seg.expr, resolver, diagnostics, overrides);
    }
  }
}

// --- Diagnostic plumbing ----------------------------------------------

function handleHook(
  result: Sentinel | Diagnostic[],
  diagnostics: Diagnostic[],
  overrides: Record<string, Severity>,
): void {
  if (isSentinel(result)) return;
  for (const d of result) add(diagnostics, d, overrides);
}

function add(
  diagnostics: Diagnostic[],
  diagnostic: Diagnostic,
  overrides: Record<string, Severity>,
): void {
  const defaultSev = DEFAULT_SEVERITIES[diagnostic.code] ?? diagnostic.severity;
  const severity = overrides[diagnostic.code] ?? defaultSev;
  diagnostics.push({ ...diagnostic, severity });
}
