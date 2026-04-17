/**
 * Canonical pretty-printer for rulang rules.
 *
 * Mirrors `rulang/formatter.py` — idempotent, round-trips with `parse()`.
 * Accepts either rule source text or a public-AST `Rule`.
 */

import {
  parse,
  type Action,
  type And,
  type Binary,
  type Compound,
  type Comparison,
  type Condition,
  type Existence,
  type Expr,
  type FunctionCall,
  type Literal,
  type Not,
  type NullCoalesce,
  type Or,
  type Path,
  type PathRef,
  type Return,
  type Rule,
  type SetAction,
  type Unary,
  type WorkflowCallAction,
  type WorkflowCallExpr,
} from "./ast.js";

const P_OR = 10;
const P_AND = 20;
const P_NOT = 30;
const P_COMP = 40;
const P_NULL_COALESCE = 50;
const P_ADD = 60;
const P_MUL = 70;
const P_UNARY = 80;

export function format(rule: string | Rule, entityName = "entity"): string {
  const ast = typeof rule === "string" ? parse(rule, entityName) : rule;
  return formatRule(ast);
}

export function formatAst(rule: Rule): string {
  return formatRule(rule);
}

/** Format a condition subtree to canonical string form (no surrounding rule). */
export function formatCondition(cond: Condition): string {
  return formatConditionImpl(cond, P_OR);
}

/** Format a single action to canonical string form. */
export function formatAction(action: Action): string {
  return formatActionImpl(action);
}

/** Format a path in canonical form. */
export function formatPath(path: Path): string {
  return formatPathImpl(path);
}

/** Format an expression to canonical string form. */
export function formatExpr(expr: Expr): string {
  return formatExprImpl(expr, P_OR);
}

function formatRule(rule: Rule): string {
  const cond = formatConditionImpl(rule.condition, P_OR);
  const actions = rule.actions.map(formatActionImpl).join("; ");
  return `${cond} => ${actions}`;
}

function formatConditionImpl(cond: Condition, minPrecedence: number): string {
  switch (cond.type) {
    case "or": {
      const s = `${formatConditionImpl((cond as Or).left, P_OR)} or ${formatConditionImpl((cond as Or).right, P_AND)}`;
      return minPrecedence > P_OR ? `(${s})` : s;
    }
    case "and": {
      const s = `${formatConditionImpl((cond as And).left, P_AND)} and ${formatConditionImpl((cond as And).right, P_NOT)}`;
      return minPrecedence > P_AND ? `(${s})` : s;
    }
    case "not": {
      const c = cond as Not;
      if (c.inner.type === "and" || c.inner.type === "or") {
        return `not (${formatConditionImpl(c.inner, P_OR)})`;
      }
      return `not ${formatConditionImpl(c.inner, P_NOT)}`;
    }
    case "existence": {
      const c = cond as Existence;
      return `${formatExprImpl(c.expr, P_COMP)} ${c.kind}`;
    }
    case "comparison": {
      const c = cond as Comparison;
      return `${formatExprImpl(c.left, P_COMP)} ${c.op} ${formatExprImpl(c.right, P_COMP)}`;
    }
  }
}

function formatExprImpl(expr: Expr, minPrecedence: number): string {
  switch (expr.type) {
    case "literal":
      return formatLiteralImpl(expr as Literal);
    case "pathRef":
      return formatPathImpl((expr as PathRef).path);
    case "functionCall": {
      const e = expr as FunctionCall;
      const args = e.args.map((a) => formatExprImpl(a, P_OR)).join(", ");
      return `${e.name}(${args})`;
    }
    case "workflowCallExpr": {
      const e = expr as WorkflowCallExpr;
      return formatWorkflowCallImpl(e.name, e.args);
    }
    case "unary":
      return `-${formatExprImpl((expr as Unary).expr, P_UNARY)}`;
    case "binary":
      return formatBinary(expr as Binary, minPrecedence);
    case "nullCoalesce": {
      const e = expr as NullCoalesce;
      const s = `${formatExprImpl(e.left, P_NULL_COALESCE)} ?? ${formatExprImpl(e.right, P_ADD)}`;
      return minPrecedence > P_NULL_COALESCE ? `(${s})` : s;
    }
    default: {
      const cond = expr as unknown as Condition;
      if (cond.type === "and" || cond.type === "or" || cond.type === "not" || cond.type === "comparison" || cond.type === "existence") {
        return `(${formatConditionImpl(cond, P_OR)})`;
      }
      throw new Error(`unknown expr type: ${(expr as { type: string }).type}`);
    }
  }
}

function formatBinary(expr: Binary, minPrecedence: number): string {
  let myPrec: number;
  let left: string;
  let right: string;
  if (expr.op === "+" || expr.op === "-") {
    myPrec = P_ADD;
    left = formatExprImpl(expr.left, P_ADD);
    right = formatExprImpl(expr.right, P_MUL);
  } else {
    myPrec = P_MUL;
    left = formatExprImpl(expr.left, P_MUL);
    right = formatExprImpl(expr.right, P_UNARY);
  }
  const s = `${left} ${expr.op} ${right}`;
  return minPrecedence > myPrec ? `(${s})` : s;
}

function formatLiteralImpl(lit: Literal): string {
  switch (lit.literalType) {
    case "string":
      return formatString(String(lit.value));
    case "bool":
      return lit.value ? "true" : "false";
    case "none":
      return "none";
    case "int":
      return String(Math.trunc(lit.value as number));
    case "float":
      return formatFloat(lit.value as number);
    case "list": {
      const items = (lit.value as Expr[]).map((item) => formatExprImpl(item, P_OR)).join(", ");
      return `[${items}]`;
    }
  }
}

function formatFloat(value: number): string {
  if (!Number.isFinite(value)) return String(value);
  let text = String(value);
  if (!text.includes(".") && !text.includes("e") && !text.includes("E")) {
    text += ".0";
  }
  return text;
}

function formatString(value: string): string {
  const escaped = value
    .replaceAll("\\", "\\\\")
    .replaceAll("'", "\\'")
    .replaceAll("\n", "\\n")
    .replaceAll("\t", "\\t");
  return `'${escaped}'`;
}

function formatPathImpl(path: Path): string {
  let out = path.root;
  for (const seg of path.segments) {
    if (seg.kind === "field") out += `.${seg.name}`;
    else if (seg.kind === "nullSafeField") out += `?.${seg.name}`;
    else out += `[${formatExprImpl(seg.expr, P_OR)}]`;
  }
  return out;
}

function formatWorkflowCallImpl(name: string, args: readonly Expr[]): string {
  const nameStr = formatString(name);
  if (args.length === 0) return `workflow(${nameStr})`;
  const argStrs = args.map((a) => formatExprImpl(a, P_OR)).join(", ");
  return `workflow(${nameStr}, ${argStrs})`;
}

function formatActionImpl(action: Action): string {
  switch (action.type) {
    case "set": {
      const a = action as SetAction;
      return `${formatPathImpl(a.path)} = ${formatExprImpl(a.value, P_OR)}`;
    }
    case "compound": {
      const a = action as Compound;
      return `${formatPathImpl(a.path)} ${a.op} ${formatExprImpl(a.value, P_OR)}`;
    }
    case "workflowCallAction": {
      const a = action as WorkflowCallAction;
      return formatWorkflowCallImpl(a.name, a.args);
    }
    case "return":
      return `ret ${formatExprImpl((action as Return).value, P_OR)}`;
  }
}
