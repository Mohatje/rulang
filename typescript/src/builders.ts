/**
 * Builder primitives for rulang (proposal #2).
 *
 * Mirrors `rulang/builders.py`. Consumers use these to construct ASTs
 * programmatically without regex-splitting rule strings. Pair with
 * `format()` for the text direction and `parse()` for the reverse.
 */

import type {
  Action,
  And,
  Binary,
  BinaryOp,
  Comparison,
  ComparisonOp,
  Compound,
  CompoundOp,
  Condition,
  Existence,
  Expr,
  FieldSegment,
  FunctionCall,
  IndexSegment,
  Literal,
  Not,
  NullCoalesce,
  NullSafeFieldSegment,
  Or,
  Path,
  PathRef,
  PathSegment,
  Return,
  Rule,
  SetAction,
  Unary,
  WorkflowCallAction,
  WorkflowCallExpr,
} from "./ast.js";

// --- paths --------------------------------------------------------------

export function pathOf(...parts: Array<string | number | Expr>): Path {
  if (parts.length === 0) throw new Error("pathOf() requires at least one part");
  if (parts.length === 1 && typeof parts[0] === "string" && (parts[0].includes(".") || parts[0].includes("?."))) {
    return parseDotted(parts[0]);
  }

  const root = parts[0];
  if (typeof root !== "string") {
    throw new TypeError(`path root must be a string, got ${typeof root}`);
  }

  const segments: PathSegment[] = [];
  for (let i = 1; i < parts.length; i++) {
    const part = parts[i];
    if (typeof part === "number") {
      segments.push({
        kind: "index",
        expr: { type: "literal", value: Math.trunc(part), literalType: "int" },
      } satisfies IndexSegment);
    } else if (typeof part === "string") {
      if (part.startsWith("?.")) {
        segments.push({ kind: "nullSafeField", name: part.slice(2) } satisfies NullSafeFieldSegment);
      } else {
        segments.push({ kind: "field", name: part } satisfies FieldSegment);
      }
    } else {
      segments.push({ kind: "index", expr: part } satisfies IndexSegment);
    }
  }
  return { type: "path", root, segments };
}

function parseDotted(text: string): Path {
  const segments: PathSegment[] = [];
  let i = 0;
  let rootEnd: number | null = null;
  while (i < text.length) {
    if (text[i] === ".") {
      rootEnd = i;
      break;
    }
    if (text[i] === "?" && text[i + 1] === ".") {
      rootEnd = i;
      break;
    }
    i += 1;
  }
  if (rootEnd === null) return { type: "path", root: text, segments: [] };
  const root = text.slice(0, rootEnd);
  i = rootEnd;
  while (i < text.length) {
    if (text.slice(i, i + 2) === "?.") {
      i += 2;
      let j = i;
      while (j < text.length && text[j] !== "." && text[j] !== "?") j += 1;
      segments.push({ kind: "nullSafeField", name: text.slice(i, j) });
      i = j;
    } else if (text[i] === ".") {
      i += 1;
      let j = i;
      while (j < text.length && text[j] !== "." && text[j] !== "?") j += 1;
      segments.push({ kind: "field", name: text.slice(i, j) });
      i = j;
    } else {
      break;
    }
  }
  return { type: "path", root, segments };
}

// --- literals / expressions --------------------------------------------

export function lit(value: unknown): Literal {
  if (value === null || value === undefined) return { type: "literal", value: null, literalType: "none" };
  if (typeof value === "boolean") return { type: "literal", value, literalType: "bool" };
  if (typeof value === "number") {
    return Number.isInteger(value)
      ? { type: "literal", value, literalType: "int" }
      : { type: "literal", value, literalType: "float" };
  }
  if (typeof value === "string") return { type: "literal", value, literalType: "string" };
  if (Array.isArray(value)) {
    return { type: "literal", value: value.map(asExpr), literalType: "list" };
  }
  throw new TypeError(`lit() does not accept values of type ${typeof value}`);
}

function asExpr(value: unknown): Expr {
  if (isAstExpr(value)) return value as Expr;
  if (isPath(value)) return { type: "pathRef", path: value as Path } satisfies PathRef;
  return lit(value);
}

function isAstExpr(v: unknown): boolean {
  if (!v || typeof v !== "object") return false;
  const t = (v as { type?: string }).type;
  return t === "literal" || t === "pathRef" || t === "functionCall" || t === "binary" ||
    t === "nullCoalesce" || t === "unary" || t === "workflowCallExpr";
}

function isPath(v: unknown): boolean {
  return !!v && typeof v === "object" && (v as { type?: string }).type === "path";
}

export function pathref(path: string | Path): PathRef {
  return { type: "pathRef", path: typeof path === "string" ? pathOf(path) : path };
}

export function fn(name: string, ...args: unknown[]): FunctionCall {
  return { type: "functionCall", name, args: args.map(asExpr) };
}

export function binary(left: unknown, op: BinaryOp, right: unknown): Binary {
  if (!["+", "-", "*", "/", "%"].includes(op)) {
    throw new Error(`invalid binary op: ${op}`);
  }
  return { type: "binary", left: asExpr(left), op, right: asExpr(right) };
}

export function unary(inner: unknown): Unary {
  return { type: "unary", op: "-", expr: asExpr(inner) };
}

export function nullCoalesce(left: unknown, right: unknown): NullCoalesce {
  return { type: "nullCoalesce", left: asExpr(left), right: asExpr(right) };
}

export function workflowExpr(name: string, ...args: unknown[]): WorkflowCallExpr {
  return { type: "workflowCallExpr", name, args: args.map(asExpr) };
}

// --- comparisons -------------------------------------------------------

function cmp(op: ComparisonOp, left: unknown, right: unknown): Comparison {
  return { type: "comparison", left: asExpr(left), op, right: asExpr(right) };
}

export const eq = (l: unknown, r: unknown) => cmp("==", l, r);
export const neq = (l: unknown, r: unknown) => cmp("!=", l, r);
export const lt = (l: unknown, r: unknown) => cmp("<", l, r);
export const gt = (l: unknown, r: unknown) => cmp(">", l, r);
export const lte = (l: unknown, r: unknown) => cmp("<=", l, r);
export const gte = (l: unknown, r: unknown) => cmp(">=", l, r);
export const inOp = (l: unknown, r: unknown) => cmp("in", l, r);
export const notIn = (l: unknown, r: unknown) => cmp("not in", l, r);
export const contains = (l: unknown, r: unknown) => cmp("contains", l, r);
export const notContains = (l: unknown, r: unknown) => cmp("not contains", l, r);
export const startswith = (l: unknown, r: unknown) => cmp("startswith", l, r);
export const endswith = (l: unknown, r: unknown) => cmp("endswith", l, r);
export const matches = (l: unknown, r: unknown) => cmp("matches", l, r);
export const containsAny = (l: unknown, r: unknown) => cmp("contains_any", l, r);
export const containsAll = (l: unknown, r: unknown) => cmp("contains_all", l, r);

export function exists(expr: unknown): Existence {
  return { type: "existence", expr: asExpr(expr), kind: "exists" };
}

export function isEmpty(expr: unknown): Existence {
  return { type: "existence", expr: asExpr(expr), kind: "is_empty" };
}

// --- logical -----------------------------------------------------------

export function and(...conditions: Condition[]): Condition {
  if (conditions.length < 2) throw new Error("and() requires at least two conditions");
  let result = conditions[0];
  for (let i = 1; i < conditions.length; i++) {
    result = { type: "and", left: result, right: conditions[i] } satisfies And;
  }
  return result;
}

export function or(...conditions: Condition[]): Condition {
  if (conditions.length < 2) throw new Error("or() requires at least two conditions");
  let result = conditions[0];
  for (let i = 1; i < conditions.length; i++) {
    result = { type: "or", left: result, right: conditions[i] } satisfies Or;
  }
  return result;
}

export function not(condition: Condition): Not {
  return { type: "not", inner: condition };
}

// --- actions -----------------------------------------------------------

function asPath(p: string | Path): Path {
  return typeof p === "string" ? pathOf(p) : p;
}

export function set_(path: string | Path, value: unknown): SetAction {
  return { type: "set", path: asPath(path), value: asExpr(value) };
}

export function compound(path: string | Path, op: CompoundOp, value: unknown): Compound {
  if (!["+=", "-=", "*=", "/="].includes(op)) throw new Error(`invalid compound op: ${op}`);
  return { type: "compound", path: asPath(path), op, value: asExpr(value) };
}

export function workflowCall(name: string, ...args: unknown[]): WorkflowCallAction {
  return { type: "workflowCallAction", name, args: args.map(asExpr) };
}

export function ret(value: unknown): Return {
  return { type: "return", value: asExpr(value) };
}

// --- rule --------------------------------------------------------------

export function rule(
  condition: Condition,
  actions: readonly Action[],
  options: { entityName?: string } = {},
): Rule {
  const entityName = options.entityName ?? "entity";
  const { reads, writes, workflowCalls } = extractReadsWrites(condition, actions, entityName);
  return {
    type: "rule",
    condition,
    actions,
    source: "",
    entityName,
    reads,
    writes,
    workflowCalls,
  };
}

// Re-derive reads/writes from the AST so builder-built rules carry the same
// extractor values as parsed rules.
function extractReadsWrites(
  condition: Condition,
  actions: readonly Action[],
  entityName: string,
): { reads: Set<string>; writes: Set<string>; workflowCalls: Set<string> } {
  const reads = new Set<string>();
  const writes = new Set<string>();
  const workflowCalls = new Set<string>();

  const pathStr = (p: Path): string => {
    const parts: string[] = [p.root];
    for (const s of p.segments) {
      if (s.kind === "field" || s.kind === "nullSafeField") parts.push(s.name);
      else parts.push("[*]");
    }
    if (parts[0] !== entityName) parts.unshift(entityName);
    return parts.join(".");
  };

  const collectReads = (e: Expr): void => {
    switch (e.type) {
      case "pathRef":
        reads.add(pathStr(e.path));
        for (const s of e.path.segments) if (s.kind === "index") collectReads(s.expr);
        return;
      case "functionCall":
        for (const a of e.args) collectReads(a);
        return;
      case "binary":
      case "nullCoalesce":
        collectReads(e.left);
        collectReads(e.right);
        return;
      case "unary":
        collectReads(e.expr);
        return;
      case "workflowCallExpr":
        workflowCalls.add(e.name);
        for (const a of e.args) collectReads(a);
        return;
      case "literal":
        if (e.literalType === "list") for (const item of e.value as Expr[]) collectReads(item);
        return;
    }
  };

  const walk = (c: Condition): void => {
    switch (c.type) {
      case "and":
      case "or":
        walk(c.left);
        walk(c.right);
        return;
      case "not":
        walk(c.inner);
        return;
      case "comparison":
        collectReads(c.left);
        collectReads(c.right);
        return;
      case "existence":
        collectReads(c.expr);
        return;
    }
  };

  walk(condition);

  for (const action of actions) {
    switch (action.type) {
      case "set":
        writes.add(pathStr(action.path));
        collectReads(action.value);
        for (const s of action.path.segments) if (s.kind === "index") collectReads(s.expr);
        break;
      case "compound": {
        const ps = pathStr(action.path);
        writes.add(ps);
        reads.add(ps);
        collectReads(action.value);
        for (const s of action.path.segments) if (s.kind === "index") collectReads(s.expr);
        break;
      }
      case "workflowCallAction":
        workflowCalls.add(action.name);
        for (const a of action.args) collectReads(a);
        break;
      case "return":
        collectReads(action.value);
        break;
    }
  }

  return { reads, writes, workflowCalls };
}
