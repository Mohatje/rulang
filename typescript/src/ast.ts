/**
 * Public AST for rulang rules.
 *
 * Mirrors the Python AST in `rulang/ast.py`. Produced from the ANTLR parse
 * tree; the primary extension point for downstream features (validation,
 * conflict detection, formatting, rule-builder tooling).
 *
 * Every AST node carries a source span so diagnostics can point into source
 * text.
 *
 * Usage:
 *   import { parse, walk } from "rulang";
 *   const rule = parse("entity.age >= 18 => entity.isAdult = true");
 *   rule.reads          // Set { "entity.age" }
 *   rule.writes         // Set { "entity.isAdult" }
 *   rule.condition      // { type: "comparison", ... }
 *   rule.actions        // [ { type: "set", ... } ]
 */

import { CommonTokenStream, InputStream, type Token } from "antlr4";
import BusinessRulesLexer from "./generated/BusinessRulesLexer.js";
import BusinessRulesParser, {
  type Rule_Context,
} from "./generated/BusinessRulesParser.js";
import { RuleSyntaxError } from "./errors.js";

// --- Spans ---------------------------------------------------------------

export interface Span {
  /** character offset, inclusive */
  readonly start: number;
  /** character offset, exclusive */
  readonly end: number;
  /** 1-based */
  readonly line: number;
  /** 1-based, at start */
  readonly column: number;
}

// --- Path ----------------------------------------------------------------

export interface FieldSegment {
  readonly kind: "field";
  readonly name: string;
}

export interface NullSafeFieldSegment {
  readonly kind: "nullSafeField";
  readonly name: string;
}

export interface IndexSegment {
  readonly kind: "index";
  readonly expr: Expr;
}

export type PathSegment = FieldSegment | NullSafeFieldSegment | IndexSegment;

export interface Path {
  readonly type: "path";
  /** the IDENTIFIER at the start of the path */
  readonly root: string;
  readonly segments: readonly PathSegment[];
  readonly span?: Span;
}

export function pathToString(
  path: Path,
  options: { normalizeEntity?: string | null; includeIndices?: boolean } = {},
): string {
  const { normalizeEntity = "entity", includeIndices = false } = options;
  const parts: string[] = [path.root];
  for (const seg of path.segments) {
    if (seg.kind === "field" || seg.kind === "nullSafeField") {
      parts.push(seg.name);
    } else {
      parts.push(includeIndices ? `[${renderIndexExpr(seg.expr)}]` : "[*]");
    }
  }
  if (normalizeEntity !== null && normalizeEntity !== undefined && parts[0] !== normalizeEntity) {
    parts.unshift(normalizeEntity);
  }
  return parts.join(".");
}

function renderIndexExpr(expr: Expr): string {
  if (expr.type === "literal") {
    if (expr.literalType === "string") return `'${String(expr.value)}'`;
    return String(expr.value);
  }
  if (expr.type === "pathRef") {
    return pathToString(expr.path, { normalizeEntity: null, includeIndices: true });
  }
  return "?";
}

// --- Literal types -------------------------------------------------------

export type LiteralType = "string" | "int" | "float" | "bool" | "none" | "list";

// --- Expressions ---------------------------------------------------------

export interface Literal {
  readonly type: "literal";
  readonly value: unknown;
  readonly literalType: LiteralType;
  readonly span?: Span;
}

export interface PathRef {
  readonly type: "pathRef";
  readonly path: Path;
  readonly span?: Span;
}

export interface FunctionCall {
  readonly type: "functionCall";
  readonly name: string;
  readonly args: readonly Expr[];
  readonly span?: Span;
}

export type BinaryOp = "+" | "-" | "*" | "/" | "%";

export interface Binary {
  readonly type: "binary";
  readonly left: Expr;
  readonly op: BinaryOp;
  readonly right: Expr;
  readonly span?: Span;
}

export interface NullCoalesce {
  readonly type: "nullCoalesce";
  readonly left: Expr;
  readonly right: Expr;
  readonly span?: Span;
}

export interface Unary {
  readonly type: "unary";
  readonly op: "-";
  readonly expr: Expr;
  readonly span?: Span;
}

export interface WorkflowCallExpr {
  readonly type: "workflowCallExpr";
  readonly name: string;
  readonly args: readonly Expr[];
  readonly span?: Span;
}

export type Expr = Literal | PathRef | FunctionCall | Binary | NullCoalesce | Unary | WorkflowCallExpr;

// --- Conditions ----------------------------------------------------------

export type ComparisonOp =
  | "=="
  | "!="
  | "<"
  | ">"
  | "<="
  | ">="
  | "in"
  | "not in"
  | "contains"
  | "not contains"
  | "startswith"
  | "endswith"
  | "matches"
  | "contains_any"
  | "contains_all";

export interface Comparison {
  readonly type: "comparison";
  readonly left: Expr;
  readonly op: ComparisonOp;
  readonly right: Expr;
  readonly span?: Span;
}

export type ExistenceKind = "exists" | "is_empty";

export interface Existence {
  readonly type: "existence";
  readonly expr: Expr;
  readonly kind: ExistenceKind;
  readonly span?: Span;
}

export interface And {
  readonly type: "and";
  readonly left: Condition;
  readonly right: Condition;
  readonly span?: Span;
}

export interface Or {
  readonly type: "or";
  readonly left: Condition;
  readonly right: Condition;
  readonly span?: Span;
}

export interface Not {
  readonly type: "not";
  readonly inner: Condition;
  readonly span?: Span;
}

export type Condition = And | Or | Not | Comparison | Existence;

// --- Actions -------------------------------------------------------------

export interface SetAction {
  readonly type: "set";
  readonly path: Path;
  readonly value: Expr;
  readonly span?: Span;
}

export type CompoundOp = "+=" | "-=" | "*=" | "/=";

export interface Compound {
  readonly type: "compound";
  readonly path: Path;
  readonly op: CompoundOp;
  readonly value: Expr;
  readonly span?: Span;
}

export interface WorkflowCallAction {
  readonly type: "workflowCallAction";
  readonly name: string;
  readonly args: readonly Expr[];
  readonly span?: Span;
}

export interface Return {
  readonly type: "return";
  readonly value: Expr;
  readonly span?: Span;
}

export type Action = SetAction | Compound | WorkflowCallAction | Return;

// --- Rule ----------------------------------------------------------------

export interface Rule {
  readonly type: "rule";
  readonly condition: Condition;
  readonly actions: readonly Action[];
  readonly source: string;
  readonly entityName: string;
  readonly span?: Span;
  readonly reads: ReadonlySet<string>;
  readonly writes: ReadonlySet<string>;
  readonly workflowCalls: ReadonlySet<string>;
}

export function ruleLiterals(rule: Rule): Literal[] {
  const out: Literal[] = [];
  walk(rule, (n) => {
    if (isAstNode(n) && n.type === "literal") out.push(n);
  });
  return out;
}

// --- Walker --------------------------------------------------------------

type AnyNode = Rule | Condition | Expr | Action | Path;

function isAstNode(v: unknown): v is AnyNode {
  return !!v && typeof v === "object" && typeof (v as { type?: unknown }).type === "string";
}

export function walk(node: unknown, visitor: (n: AnyNode) => void): void {
  for (const child of iterAst(node)) {
    visitor(child);
    walk(child, visitor);
  }
}

function* iterAst(node: unknown): Generator<AnyNode> {
  if (!isAstNode(node)) return;
  switch (node.type) {
    case "rule":
      yield node.condition;
      for (const a of node.actions) yield a;
      return;
    case "and":
    case "or":
      yield node.left;
      yield node.right;
      return;
    case "not":
      yield node.inner;
      return;
    case "comparison":
      yield node.left;
      yield node.right;
      return;
    case "existence":
      yield node.expr;
      return;
    case "set":
      yield node.path;
      yield node.value;
      return;
    case "compound":
      yield node.path;
      yield node.value;
      return;
    case "workflowCallAction":
      for (const a of node.args) yield a;
      return;
    case "return":
      yield node.value;
      return;
    case "pathRef":
      yield node.path;
      return;
    case "functionCall":
      for (const a of node.args) yield a;
      return;
    case "binary":
      yield node.left;
      yield node.right;
      return;
    case "nullCoalesce":
      yield node.left;
      yield node.right;
      return;
    case "unary":
      yield node.expr;
      return;
    case "workflowCallExpr":
      for (const a of node.args) yield a;
      return;
    case "path":
      for (const s of node.segments) {
        if (s.kind === "index") yield s.expr;
      }
      return;
    case "literal":
      return;
  }
}

// --- parse() -------------------------------------------------------------

class SyntaxErrorListener {
  public readonly errors: Array<[number, number, string]> = [];

  constructor(public readonly source: string) {}

  public syntaxError(
    _recognizer: unknown,
    _offendingSymbol: Token,
    line: number,
    column: number,
    msg: string,
  ): void {
    this.errors.push([line, column, msg]);
  }
}

function spanOf(ctx: unknown): Span | undefined {
  const withRange = ctx as { start?: { start: number; line: number; column: number }; stop?: { stop: number } };
  const start = withRange.start;
  const stop = withRange.stop;
  if (!start || !stop) return undefined;
  return {
    start: start.start,
    end: stop.stop !== undefined ? stop.stop + 1 : start.start,
    line: start.line,
    column: start.column + 1,
  };
}

export function parse(source: string, entityName = "entity"): Rule {
  const inputStream = new InputStream(source) as unknown;
  const lexer = new BusinessRulesLexer(inputStream as never);
  const tokenStream = new CommonTokenStream(lexer as never) as unknown;
  const parser = new BusinessRulesParser(tokenStream as never);
  const listener = new SyntaxErrorListener(source);

  (lexer as unknown as { removeErrorListeners(): void }).removeErrorListeners();
  (lexer as unknown as { addErrorListener(l: object): void }).addErrorListener(listener);
  (parser as unknown as { removeErrorListeners(): void }).removeErrorListeners();
  (parser as unknown as { addErrorListener(l: object): void }).addErrorListener(listener);

  const tree = parser.rule_();
  if (listener.errors.length > 0) {
    const [line, column, message] = listener.errors[0];
    throw new RuleSyntaxError(source, message, line, column);
  }

  return buildRule(tree, source, entityName);
}

function asCondition(node: AnyNode): Condition {
  switch (node.type) {
    case "and":
    case "or":
    case "not":
    case "comparison":
    case "existence":
      return node;
    default:
      return {
        type: "comparison",
        left: node as Expr,
        op: "==",
        right: { type: "literal", value: true, literalType: "bool" } as Literal,
        span: (node as { span?: Span }).span,
      };
  }
}

function asExpr(node: AnyNode): Expr {
  if (node.type === "comparison") {
    const r = node.right;
    if (node.op === "==" && r.type === "literal" && r.literalType === "bool" && r.value === true && r.span === undefined) {
      return node.left;
    }
  }
  return node as Expr;
}

function buildRule(ctx: Rule_Context, source: string, entityName: string): Rule {
  const condition = asCondition(buildOr(ctx.condition().orExpr()));
  const actions = ctx.actions().action_list().map((a: unknown) => buildAction(a));
  const { reads, writes, workflowCalls } = extractReadsWrites(condition, actions, entityName);
  return {
    type: "rule",
    condition,
    actions,
    source,
    entityName,
    span: spanOf(ctx),
    reads,
    writes,
    workflowCalls,
  };
}

function buildOr(ctx: unknown): AnyNode {
  const c = ctx as { andExpr_list(): unknown[] };
  const children = c.andExpr_list();
  if (children.length === 1) return buildAnd(children[0]);
  let result: AnyNode = asCondition(buildAnd(children[0]));
  for (let i = 1; i < children.length; i++) {
    result = {
      type: "or",
      left: result as Condition,
      right: asCondition(buildAnd(children[i])),
      span: spanOf(ctx),
    };
  }
  return result;
}

function buildAnd(ctx: unknown): AnyNode {
  const c = ctx as { notExpr_list(): unknown[] };
  const children = c.notExpr_list();
  if (children.length === 1) return buildNot(children[0]);
  let result: AnyNode = asCondition(buildNot(children[0]));
  for (let i = 1; i < children.length; i++) {
    result = {
      type: "and",
      left: result as Condition,
      right: asCondition(buildNot(children[i])),
      span: spanOf(ctx),
    };
  }
  return result;
}

function buildNot(ctx: unknown): AnyNode {
  const c = ctx as { NOT(): unknown; notExpr(): unknown; comparison(): unknown };
  if (c.NOT()) {
    const inner = asCondition(buildNot(c.notExpr()));
    return { type: "not", inner, span: spanOf(ctx) };
  }
  return buildComparison(c.comparison());
}

const COMP_OP_TOKENS: Array<[string, ComparisonOp]> = [
  ["EQ", "=="],
  ["NEQ", "!="],
  ["LTE", "<="],
  ["GTE", ">="],
  ["LT", "<"],
  ["GT", ">"],
  ["NOT_IN", "not in"],
  ["IN", "in"],
  ["NOT_CONTAINS", "not contains"],
  ["CONTAINS_ANY", "contains_any"],
  ["CONTAINS_ALL", "contains_all"],
  ["CONTAINS", "contains"],
  ["STARTS_WITH", "startswith"],
  ["ENDS_WITH", "endswith"],
  ["MATCHES", "matches"],
];

function comparisonOp(ctx: unknown): ComparisonOp {
  const c = ctx as Record<string, () => unknown>;
  for (const [tokenName, op] of COMP_OP_TOKENS) {
    const fn = c[tokenName];
    if (typeof fn === "function" && fn.call(ctx)) return op;
  }
  return "==";
}

function buildComparison(ctx: unknown): AnyNode {
  const c = ctx as {
    nullCoalesce_list(): unknown[];
    IS_EMPTY(): unknown;
    EXISTS(): unknown;
  };
  const operands = c.nullCoalesce_list();
  const left = buildNullCoalesce(operands[0]);
  if (c.IS_EMPTY()) {
    return { type: "existence", expr: asExpr(left), kind: "is_empty", span: spanOf(ctx) };
  }
  if (c.EXISTS()) {
    return { type: "existence", expr: asExpr(left), kind: "exists", span: spanOf(ctx) };
  }
  if (operands.length === 1) return left;
  const right = buildNullCoalesce(operands[1]);
  return {
    type: "comparison",
    left: asExpr(left),
    op: comparisonOp(ctx),
    right: asExpr(right),
    span: spanOf(ctx),
  };
}

function buildNullCoalesce(ctx: unknown): AnyNode {
  const c = ctx as { addExpr_list(): unknown[] };
  const operands = c.addExpr_list();
  if (operands.length === 1) return buildAddExpr(operands[0]);
  let result: AnyNode = asExpr(buildAddExpr(operands[0]));
  for (let i = 1; i < operands.length; i++) {
    result = {
      type: "nullCoalesce",
      left: result as Expr,
      right: asExpr(buildAddExpr(operands[i])),
      span: spanOf(ctx),
    };
  }
  return result;
}

function tokenType(child: unknown): number | undefined {
  return (child as { symbol?: { type: number } }).symbol?.type;
}

function buildAddExpr(ctx: unknown): AnyNode {
  const c = ctx as { mulExpr_list(): unknown[]; mulExpr(i: number): unknown; children?: unknown[] };
  const operands = c.mulExpr_list();
  if (operands.length === 1) return buildMulExpr(operands[0]);
  const children = c.children ?? [];
  let result: AnyNode = asExpr(buildMulExpr(operands[0]));
  let opIdx = 1;
  for (let i = 1; i < operands.length; i++) {
    while (opIdx < children.length) {
      const t = tokenType(children[opIdx]);
      if (t === BusinessRulesParser.PLUS || t === BusinessRulesParser.MINUS) break;
      opIdx += 1;
    }
    const t = tokenType(children[opIdx]);
    opIdx += 1;
    const right = asExpr(buildMulExpr(operands[i]));
    result = {
      type: "binary",
      left: result as Expr,
      op: t === BusinessRulesParser.PLUS ? "+" : "-",
      right,
      span: spanOf(ctx),
    };
  }
  return result;
}

function buildMulExpr(ctx: unknown): AnyNode {
  const c = ctx as { unaryExpr_list(): unknown[]; children?: unknown[] };
  const operands = c.unaryExpr_list();
  if (operands.length === 1) return buildUnary(operands[0]);
  const children = c.children ?? [];
  let result: AnyNode = asExpr(buildUnary(operands[0]));
  let opIdx = 1;
  for (let i = 1; i < operands.length; i++) {
    while (opIdx < children.length) {
      const t = tokenType(children[opIdx]);
      if (
        t === BusinessRulesParser.STAR ||
        t === BusinessRulesParser.SLASH ||
        t === BusinessRulesParser.MOD
      ) {
        break;
      }
      opIdx += 1;
    }
    const t = tokenType(children[opIdx]);
    opIdx += 1;
    const right = asExpr(buildUnary(operands[i]));
    let op: BinaryOp;
    if (t === BusinessRulesParser.STAR) op = "*";
    else if (t === BusinessRulesParser.SLASH) op = "/";
    else op = "%";
    result = { type: "binary", left: result as Expr, op, right, span: spanOf(ctx) };
  }
  return result;
}

function buildUnary(ctx: unknown): AnyNode {
  const c = ctx as { MINUS(): unknown; unaryExpr(): unknown; primary(): unknown };
  if (c.MINUS()) {
    const inner = asExpr(buildUnary(c.unaryExpr()));
    return { type: "unary", op: "-", expr: inner, span: spanOf(ctx) };
  }
  return buildPrimary(c.primary());
}

function buildPrimary(ctx: unknown): AnyNode {
  const c = ctx as {
    LPAREN(): unknown;
    orExpr(): unknown;
    literal(): unknown;
    functionCall(): unknown;
    path(): unknown;
    workflowCall(): unknown;
  };
  if (c.LPAREN()) return buildOr(c.orExpr());
  if (c.literal()) return buildLiteral(c.literal());
  if (c.functionCall()) return buildFunctionCall(c.functionCall());
  if (c.path()) return { type: "pathRef", path: buildPath(c.path()), span: spanOf(ctx) };
  if (c.workflowCall()) return buildWorkflowExpr(c.workflowCall());
  throw new Error("unexpected primary context");
}

function unescapeString(text: string): string {
  return text
    .slice(1, -1)
    .replaceAll("\\n", "\n")
    .replaceAll("\\t", "\t")
    .replaceAll('\\"', '"')
    .replaceAll("\\'", "'")
    .replaceAll("\\\\", "\\");
}

function buildLiteral(ctx: unknown): AnyNode {
  const c = ctx as Record<string, (() => unknown) | undefined> & { list_(): { orExpr_list(): unknown[] } | null };
  if (c.NUMBER?.()) {
    const text = (c.NUMBER() as { getText(): string }).getText();
    const isFloat = text.includes(".");
    return {
      type: "literal",
      value: isFloat ? Number.parseFloat(text) : Number.parseInt(text, 10),
      literalType: isFloat ? "float" : "int",
      span: spanOf(ctx),
    };
  }
  if (c.STRING?.()) {
    const raw = (c.STRING() as { getText(): string }).getText();
    return { type: "literal", value: unescapeString(raw), literalType: "string", span: spanOf(ctx) };
  }
  if (c.TRUE?.()) return { type: "literal", value: true, literalType: "bool", span: spanOf(ctx) };
  if (c.FALSE?.()) return { type: "literal", value: false, literalType: "bool", span: spanOf(ctx) };
  if (c.NONE?.()) return { type: "literal", value: null, literalType: "none", span: spanOf(ctx) };
  const listCtx = c.list_();
  if (listCtx) {
    const items = listCtx.orExpr_list().map((e) => asExpr(buildOr(e)));
    return { type: "literal", value: items, literalType: "list", span: spanOf(ctx) };
  }
  throw new Error("unexpected literal");
}

function buildFunctionCall(ctx: unknown): AnyNode {
  const c = ctx as { IDENTIFIER(): { getText(): string }; orExpr_list(): unknown[] };
  const name = c.IDENTIFIER().getText();
  const args = c.orExpr_list().map((e) => asExpr(buildOr(e)));
  return { type: "functionCall", name, args, span: spanOf(ctx) };
}

function buildWorkflowExpr(ctx: unknown): AnyNode {
  const c = ctx as { STRING(): { getText(): string }; orExpr_list(): unknown[] };
  const name = unescapeString(c.STRING().getText());
  const args = c.orExpr_list().map((e) => asExpr(buildOr(e)));
  return { type: "workflowCallExpr", name, args, span: spanOf(ctx) };
}

function buildPath(ctx: unknown): Path {
  const c = ctx as {
    IDENTIFIER(): { getText(): string };
    pathSegment_list(): Array<{
      DOT(): unknown;
      NULL_SAFE_DOT(): unknown;
      IDENTIFIER(): { getText(): string };
      LBRACKET(): unknown;
      orExpr(): unknown;
    }>;
  };
  const root = c.IDENTIFIER().getText();
  const segments: PathSegment[] = [];
  for (const seg of c.pathSegment_list()) {
    if (seg.DOT()) segments.push({ kind: "field", name: seg.IDENTIFIER().getText() });
    else if (seg.NULL_SAFE_DOT()) segments.push({ kind: "nullSafeField", name: seg.IDENTIFIER().getText() });
    else if (seg.LBRACKET()) segments.push({ kind: "index", expr: asExpr(buildOr(seg.orExpr())) });
  }
  return { type: "path", root, segments, span: spanOf(ctx) };
}

function buildAction(ctx: unknown): Action {
  const c = ctx as {
    returnStmt(): null | { orExpr(): unknown };
    assignment(): null | {
      path(): unknown;
      orExpr(): unknown;
      assignOp(): {
        ASSIGN(): unknown;
        PLUS_ASSIGN(): unknown;
        MINUS_ASSIGN(): unknown;
        STAR_ASSIGN(): unknown;
        SLASH_ASSIGN(): unknown;
      };
    };
    workflowCall(): null | { STRING(): { getText(): string }; orExpr_list(): unknown[] };
  };
  const ret = c.returnStmt();
  if (ret) {
    return { type: "return", value: asExpr(buildOr(ret.orExpr())), span: spanOf(ctx) };
  }
  const assign = c.assignment();
  if (assign) {
    const path = buildPath(assign.path());
    const value = asExpr(buildOr(assign.orExpr()));
    const assignOp = assign.assignOp();
    if (assignOp.ASSIGN()) return { type: "set", path, value, span: spanOf(ctx) };
    let op: CompoundOp = "+=";
    if (assignOp.PLUS_ASSIGN()) op = "+=";
    else if (assignOp.MINUS_ASSIGN()) op = "-=";
    else if (assignOp.STAR_ASSIGN()) op = "*=";
    else if (assignOp.SLASH_ASSIGN()) op = "/=";
    return { type: "compound", path, op, value, span: spanOf(ctx) };
  }
  const wf = c.workflowCall();
  if (wf) {
    const name = unescapeString(wf.STRING().getText());
    const args = wf.orExpr_list().map((e) => asExpr(buildOr(e)));
    return { type: "workflowCallAction", name, args, span: spanOf(ctx) };
  }
  throw new Error("unexpected action");
}

// --- Reads/writes extraction --------------------------------------------

function extractReadsWrites(
  condition: Condition,
  actions: readonly Action[],
  entityName: string,
): { reads: ReadonlySet<string>; writes: ReadonlySet<string>; workflowCalls: ReadonlySet<string> } {
  const reads = new Set<string>();
  const writes = new Set<string>();
  const workflowCalls = new Set<string>();

  const pathStr = (p: Path) => pathToString(p, { normalizeEntity: entityName, includeIndices: false });

  const collectReads = (e: Expr): void => {
    switch (e.type) {
      case "pathRef":
        reads.add(pathStr(e.path));
        for (const seg of e.path.segments) {
          if (seg.kind === "index") collectReads(seg.expr);
        }
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
        if (e.literalType === "list") {
          for (const item of e.value as Expr[]) collectReads(item);
        }
        return;
    }
  };

  const walkCondition = (c: Condition): void => {
    switch (c.type) {
      case "and":
      case "or":
        walkCondition(c.left);
        walkCondition(c.right);
        return;
      case "not":
        walkCondition(c.inner);
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

  walkCondition(condition);

  for (const action of actions) {
    switch (action.type) {
      case "set":
        writes.add(pathStr(action.path));
        collectReads(action.value);
        for (const seg of action.path.segments) {
          if (seg.kind === "index") collectReads(seg.expr);
        }
        break;
      case "compound": {
        const ps = pathStr(action.path);
        writes.add(ps);
        reads.add(ps);
        collectReads(action.value);
        for (const seg of action.path.segments) {
          if (seg.kind === "index") collectReads(seg.expr);
        }
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
