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

function formatRule(rule: Rule): string {
  const cond = formatCondition(rule.condition, P_OR);
  const actions = rule.actions.map(formatAction).join("; ");
  return `${cond} => ${actions}`;
}

function formatCondition(cond: Condition, minPrecedence: number): string {
  switch (cond.type) {
    case "or": {
      const s = `${formatCondition((cond as Or).left, P_OR)} or ${formatCondition((cond as Or).right, P_AND)}`;
      return minPrecedence > P_OR ? `(${s})` : s;
    }
    case "and": {
      const s = `${formatCondition((cond as And).left, P_AND)} and ${formatCondition((cond as And).right, P_NOT)}`;
      return minPrecedence > P_AND ? `(${s})` : s;
    }
    case "not": {
      const c = cond as Not;
      if (c.inner.type === "and" || c.inner.type === "or") {
        return `not (${formatCondition(c.inner, P_OR)})`;
      }
      return `not ${formatCondition(c.inner, P_NOT)}`;
    }
    case "existence": {
      const c = cond as Existence;
      return `${formatExpr(c.expr, P_COMP)} ${c.kind}`;
    }
    case "comparison": {
      const c = cond as Comparison;
      return `${formatExpr(c.left, P_COMP)} ${c.op} ${formatExpr(c.right, P_COMP)}`;
    }
  }
}

function formatExpr(expr: Expr, minPrecedence: number): string {
  switch (expr.type) {
    case "literal":
      return formatLiteral(expr as Literal);
    case "pathRef":
      return formatPath((expr as PathRef).path);
    case "functionCall": {
      const e = expr as FunctionCall;
      const args = e.args.map((a) => formatExpr(a, P_OR)).join(", ");
      return `${e.name}(${args})`;
    }
    case "workflowCallExpr": {
      const e = expr as WorkflowCallExpr;
      return formatWorkflowCall(e.name, e.args);
    }
    case "unary":
      return `-${formatExpr((expr as Unary).expr, P_UNARY)}`;
    case "binary":
      return formatBinary(expr as Binary, minPrecedence);
    case "nullCoalesce": {
      const e = expr as NullCoalesce;
      const s = `${formatExpr(e.left, P_NULL_COALESCE)} ?? ${formatExpr(e.right, P_ADD)}`;
      return minPrecedence > P_NULL_COALESCE ? `(${s})` : s;
    }
    default: {
      // Conditions-as-expressions: parenthesize as a logical condition
      const cond = expr as unknown as Condition;
      if (cond.type === "and" || cond.type === "or" || cond.type === "not" || cond.type === "comparison" || cond.type === "existence") {
        return `(${formatCondition(cond, P_OR)})`;
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
    left = formatExpr(expr.left, P_ADD);
    right = formatExpr(expr.right, P_MUL);
  } else {
    myPrec = P_MUL;
    left = formatExpr(expr.left, P_MUL);
    right = formatExpr(expr.right, P_UNARY);
  }
  const s = `${left} ${expr.op} ${right}`;
  return minPrecedence > myPrec ? `(${s})` : s;
}

function formatLiteral(lit: Literal): string {
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
      const items = (lit.value as Expr[]).map((item) => formatExpr(item, P_OR)).join(", ");
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

function formatPath(path: Path): string {
  let out = path.root;
  for (const seg of path.segments) {
    if (seg.kind === "field") out += `.${seg.name}`;
    else if (seg.kind === "nullSafeField") out += `?.${seg.name}`;
    else out += `[${formatExpr(seg.expr, P_OR)}]`;
  }
  return out;
}

function formatWorkflowCall(name: string, args: readonly Expr[]): string {
  const nameStr = formatString(name);
  if (args.length === 0) return `workflow(${nameStr})`;
  const argStrs = args.map((a) => formatExpr(a, P_OR)).join(", ");
  return `workflow(${nameStr}, ${argStrs})`;
}

function formatAction(action: Action): string {
  switch (action.type) {
    case "set": {
      const a = action as SetAction;
      return `${formatPath(a.path)} = ${formatExpr(a.value, P_OR)}`;
    }
    case "compound": {
      const a = action as Compound;
      return `${formatPath(a.path)} ${a.op} ${formatExpr(a.value, P_OR)}`;
    }
    case "workflowCallAction": {
      const a = action as WorkflowCallAction;
      return formatWorkflowCall(a.name, a.args);
    }
    case "return":
      return `ret ${formatExpr((action as Return).value, P_OR)}`;
  }
}
