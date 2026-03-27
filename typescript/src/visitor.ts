import {
  CommonTokenStream,
  InputStream,
  Token,
} from "antlr4";
import { isDeepStrictEqual } from "node:util";
import BusinessRulesLexer from "./generated/BusinessRulesLexer.js";
import BusinessRulesParser, {
  ActionContext,
  ActionsContext,
  AddExprContext,
  AndExprContext,
  AssignmentContext,
  ComparisonContext,
  ConditionContext,
  FunctionCallContext,
  List_Context,
  LiteralContext,
  MulExprContext,
  NotExprContext,
  NullCoalesceContext,
  OrExprContext,
  PathContext,
  PrimaryContext,
  ReturnStmtContext,
  Rule_Context,
  UnaryExprContext,
  WorkflowCallContext,
} from "./generated/BusinessRulesParser.js";
import BusinessRulesVisitor from "./generated/BusinessRulesVisitor.js";
import {
  EvaluationError,
  PathResolutionError,
  RuleSyntaxError,
  WorkflowNotFoundError,
} from "./errors.js";
import { PathResolver } from "./pathResolver.js";
import { Workflow, type WorkflowLike } from "./workflows.js";

type PathPart = string | number;

function pythonTruthiness(value: unknown): boolean {
  if (value === null || value === undefined) {
    return false;
  }
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number") {
    return value !== 0 && !Number.isNaN(value);
  }
  if (typeof value === "bigint") {
    return value !== 0n;
  }
  if (typeof value === "string") {
    return value.length > 0;
  }
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  if (value instanceof Set || value instanceof Map) {
    return value.size > 0;
  }
  if (typeof value === "object") {
    return Object.keys(value as Record<string, unknown>).length > 0;
  }
  return true;
}

function pythonRound(value: number, digits = 0): number {
  const factor = 10 ** digits;
  const scaled = value * factor;
  const floorValue = Math.floor(scaled);
  const diff = scaled - floorValue;

  let rounded: number;
  if (diff > 0.5) {
    rounded = floorValue + 1;
  } else if (diff < 0.5) {
    rounded = floorValue;
  } else {
    rounded = floorValue % 2 === 0 ? floorValue : floorValue + 1;
  }

  const result = rounded / factor;
  return digits === 0 ? Math.trunc(result) : Number(result.toFixed(digits));
}

function mapKeys(value: unknown): string[] {
  if (value instanceof Map) {
    return [...value.keys()].map(String);
  }
  if (value && typeof value === "object") {
    return Object.keys(value as Record<string, unknown>);
  }
  return [];
}

function mapValues(value: unknown): unknown[] {
  if (value instanceof Map) {
    return [...value.values()];
  }
  if (value && typeof value === "object") {
    return Object.values(value as Record<string, unknown>);
  }
  return [];
}

function addValues(left: unknown, right: unknown): unknown {
  if (Array.isArray(left) && Array.isArray(right)) {
    return [...left, ...right];
  }
  if (typeof left === "string" || typeof right === "string") {
    return `${left ?? ""}${right ?? ""}`;
  }
  return Number(left) + Number(right);
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

const BUILTIN_FUNCTIONS: Record<string, (...args: unknown[]) => unknown> = {
  lower: (value) => (value === null || value === undefined ? null : String(value).toLowerCase()),
  upper: (value) => (value === null || value === undefined ? null : String(value).toUpperCase()),
  trim: (value) => (value === null || value === undefined ? null : String(value).trim()),
  strip: (value) => (value === null || value === undefined ? null : String(value).trim()),
  int: (value) => (value === null || value === undefined ? null : Math.trunc(Number.parseFloat(String(value)))),
  float: (value) => (value === null || value === undefined ? null : Number.parseFloat(String(value))),
  str: (value) => (value === null || value === undefined ? null : String(value)),
  bool: (value) => pythonTruthiness(value),
  len: (value) => {
    if (value === null || value === undefined) {
      return 0;
    }
    if (typeof value === "string" || Array.isArray(value)) {
      return value.length;
    }
    if (value instanceof Set || value instanceof Map) {
      return value.size;
    }
    if (typeof value === "object") {
      return Object.keys(value as Record<string, unknown>).length;
    }
    return 0;
  },
  first: (value) => (Array.isArray(value) && value.length > 0 ? value[0] : null),
  last: (value) => (Array.isArray(value) && value.length > 0 ? value[value.length - 1] : null),
  keys: (value) => mapKeys(value),
  values: (value) => mapValues(value),
  abs: (value) => (value === null || value === undefined ? null : Math.abs(Number(value))),
  round: (value, digits = 0) =>
    value === null || value === undefined ? null : pythonRound(Number(value), Number(digits)),
  min: (...args) => (args.length === 0 ? null : Math.min(...args.map((arg) => Number(arg)))),
  max: (...args) => (args.length === 0 ? null : Math.max(...args.map((arg) => Number(arg)))),
  is_list: (value) => Array.isArray(value),
  is_string: (value) => typeof value === "string",
  is_number: (value) => typeof value === "number",
  is_none: (value) => value === null || value === undefined,
};

class RuleSyntaxErrorListener {
  public readonly errors: Array<[number, number, string]> = [];

  public constructor(public readonly ruleText: string) {}

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

export interface ParsedRule {
  ruleText: string;
  tree: Rule_Context;
  reads: Set<string>;
  writes: Set<string>;
  workflowCalls: Set<string>;
}

class ReturnValue extends Error {
  public constructor(public readonly value: unknown) {
    super("ReturnValue");
  }
}

class BaseRuleVisitor<Result> extends BusinessRulesVisitor<Result> {
  public visitNode<T>(ctx: { accept(visitor: BusinessRulesVisitor<T>): T }): T {
    return ctx.accept(this as unknown as BusinessRulesVisitor<T>);
  }
}

export class RuleAnalyzer extends BaseRuleVisitor<void> {
  public readonly reads = new Set<string>();
  public readonly writes = new Set<string>();
  public readonly workflowCalls = new Set<string>();
  private inCondition = false;
  private inAssignmentTarget = false;

  public constructor(private readonly entityName = "entity") {
    super();
  }

  public readonly visitRule_ = (ctx: Rule_Context): void => {
    this.inCondition = true;
    this.visitNode(ctx.condition());
    this.inCondition = false;
    this.visitNode(ctx.actions());
  };

  public readonly visitCondition = (ctx: ConditionContext): void => {
    this.visitNode(ctx.orExpr());
  };

  public readonly visitOrExpr = (ctx: OrExprContext): void => {
    ctx.andExpr_list().forEach((child: AndExprContext) => this.visitNode(child));
  };

  public readonly visitAndExpr = (ctx: AndExprContext): void => {
    ctx.notExpr_list().forEach((child: NotExprContext) => this.visitNode(child));
  };

  public readonly visitNotExpr = (ctx: NotExprContext): void => {
    if (ctx.NOT()) {
      this.visitNode(ctx.notExpr());
      return;
    }
    this.visitNode(ctx.comparison());
  };

  public readonly visitComparison = (ctx: ComparisonContext): void => {
    ctx.nullCoalesce_list().forEach((child: NullCoalesceContext) => this.visitNode(child));
  };

  public readonly visitNullCoalesce = (ctx: NullCoalesceContext): void => {
    ctx.addExpr_list().forEach((child: AddExprContext) => this.visitNode(child));
  };

  public readonly visitAddExpr = (ctx: AddExprContext): void => {
    ctx.mulExpr_list().forEach((child: MulExprContext) => this.visitNode(child));
  };

  public readonly visitMulExpr = (ctx: MulExprContext): void => {
    ctx.unaryExpr_list().forEach((child: UnaryExprContext) => this.visitNode(child));
  };

  public readonly visitUnaryExpr = (ctx: UnaryExprContext): void => {
    if (ctx.MINUS()) {
      this.visitNode(ctx.unaryExpr());
      return;
    }
    this.visitNode(ctx.primary());
  };

  public readonly visitPrimary = (ctx: PrimaryContext): void => {
    if (ctx.LPAREN()) {
      this.visitNode(ctx.orExpr());
    } else if (ctx.literal()) {
      this.visitNode(ctx.literal());
    } else if (ctx.functionCall()) {
      this.visitNode(ctx.functionCall());
    } else if (ctx.path()) {
      this.visitNode(ctx.path());
    } else if (ctx.workflowCall()) {
      this.visitNode(ctx.workflowCall());
    }
  };

  public readonly visitFunctionCall = (ctx: FunctionCallContext): void => {
    ctx.orExpr_list().forEach((child: OrExprContext) => this.visitNode(child));
  };

  public readonly visitLiteral = (ctx: LiteralContext): void => {
    if (ctx.list_()) {
      this.visitNode(ctx.list_());
    }
  };

  public readonly visitList_ = (ctx: List_Context): void => {
    ctx.orExpr_list().forEach((child: OrExprContext) => this.visitNode(child));
  };

  public readonly visitPath = (ctx: PathContext): void => {
    const path = this.getPathString(ctx);
    if (this.inCondition) {
      this.reads.add(path);
    } else if (this.inAssignmentTarget) {
      this.writes.add(path);
    } else {
      this.reads.add(path);
    }
  };

  public readonly visitWorkflowCall = (ctx: WorkflowCallContext): void => {
    const workflowName = unescapeString(ctx.STRING().getText());
    this.workflowCalls.add(workflowName);
    ctx.orExpr_list().forEach((child: OrExprContext) => this.visitNode(child));
  };

  public readonly visitActions = (ctx: ActionsContext): void => {
    ctx.action_list().forEach((child: ActionContext) => this.visitNode(child));
  };

  public readonly visitAction = (ctx: ActionContext): void => {
    if (ctx.returnStmt()) {
      this.visitNode(ctx.returnStmt());
    } else if (ctx.assignment()) {
      this.visitNode(ctx.assignment());
    } else if (ctx.workflowCall()) {
      this.visitNode(ctx.workflowCall());
    }
  };

  public readonly visitReturnStmt = (ctx: ReturnStmtContext): void => {
    this.visitNode(ctx.orExpr());
  };

  public readonly visitAssignment = (ctx: AssignmentContext): void => {
    this.inAssignmentTarget = true;
    this.visitNode(ctx.path());
    this.inAssignmentTarget = false;

    if (!ctx.assignOp().ASSIGN()) {
      this.reads.add(this.getPathString(ctx.path()));
    }

    this.visitNode(ctx.orExpr());
  };

  private getPathString(ctx: PathContext): string {
    const parts: string[] = [ctx.IDENTIFIER().getText()];

    ctx.pathSegment_list().forEach((segment: { DOT(): unknown; NULL_SAFE_DOT(): unknown; IDENTIFIER(): { getText(): string }; LBRACKET(): unknown }) => {
      if (segment.DOT() || segment.NULL_SAFE_DOT()) {
        parts.push(segment.IDENTIFIER().getText());
      } else if (segment.LBRACKET()) {
        parts.push("[*]");
      }
    });

    if (parts[0] !== this.entityName) {
      parts.unshift(this.entityName);
    }

    return parts.join(".");
  }
}

export class RuleInterpreter extends BaseRuleVisitor<unknown> {
  private readonly resolver: PathResolver;
  private returnValue: unknown = null;
  private hasReturned = false;

  public constructor(
    private readonly entity: unknown,
    private readonly workflows: Record<string, WorkflowLike> = {},
    private readonly entityName = "entity",
  ) {
    super();
    this.resolver = new PathResolver(entity, entityName);
  }

  public execute(tree: Rule_Context): [boolean, unknown] {
    try {
      return this.visitNode(tree) as [boolean, unknown];
    } catch (error) {
      if (error instanceof ReturnValue) {
        return [true, error.value];
      }
      if (error instanceof PathResolutionError || error instanceof WorkflowNotFoundError) {
        throw error;
      }
      throw new EvaluationError("", error instanceof Error ? error.message : String(error));
    }
  }

  public readonly visitRule_ = (ctx: Rule_Context): [boolean, unknown] => {
    const conditionResult = this.visitNode(ctx.condition());
    if (!pythonTruthiness(conditionResult)) {
      return [false, null];
    }

    this.visitNode(ctx.actions());
    if (this.hasReturned) {
      return [true, this.returnValue];
    }
    return [true, true];
  };

  public readonly visitCondition = (ctx: ConditionContext): unknown => this.visitNode(ctx.orExpr());

  public readonly visitOrExpr = (ctx: OrExprContext): unknown => {
    const expressions = ctx.andExpr_list();
    let result = this.visitNode(expressions[0]);

    for (let index = 1; index < expressions.length; index += 1) {
      if (pythonTruthiness(result)) {
        return result;
      }
      result = this.visitNode(expressions[index]);
    }

    return result;
  };

  public readonly visitAndExpr = (ctx: AndExprContext): unknown => {
    const expressions = ctx.notExpr_list();
    let result = this.visitNode(expressions[0]);

    for (let index = 1; index < expressions.length; index += 1) {
      if (!pythonTruthiness(result)) {
        return result;
      }
      result = this.visitNode(expressions[index]);
    }

    return result;
  };

  public readonly visitNotExpr = (ctx: NotExprContext): unknown => {
    if (ctx.NOT()) {
      return !pythonTruthiness(this.visitNode(ctx.notExpr()));
    }
    return this.visitNode(ctx.comparison());
  };

  public readonly visitComparison = (ctx: ComparisonContext): unknown => {
    const operands = ctx.nullCoalesce_list();
    const left = this.visitNode(operands[0]);

    if (ctx.IS_EMPTY()) {
      return this.isEmpty(left);
    }
    if (ctx.EXISTS()) {
      return left !== null;
    }
    if (operands.length === 1) {
      return left;
    }

    const right = this.visitNode(operands[1]);

    if (ctx.EQ()) return this.compareEq(left, right);
    if (ctx.NEQ()) return !this.compareEq(left, right);
    if (ctx.LT()) return this.compareOrder(left, right, "lt");
    if (ctx.GT()) return this.compareOrder(left, right, "gt");
    if (ctx.LTE()) return this.compareOrder(left, right, "lte");
    if (ctx.GTE()) return this.compareOrder(left, right, "gte");
    if (ctx.IN()) return this.checkIn(left, right);
    if (ctx.NOT_IN()) return !this.checkIn(left, right);
    if (ctx.CONTAINS()) return this.contains(left, right);
    if (ctx.NOT_CONTAINS()) return !this.contains(left, right);
    if (ctx.STARTS_WITH()) return this.startsWith(left, right);
    if (ctx.ENDS_WITH()) return this.endsWith(left, right);
    if (ctx.MATCHES()) return this.matches(left, right);
    if (ctx.CONTAINS_ANY()) return this.containsAny(left, right);
    if (ctx.CONTAINS_ALL()) return this.containsAll(left, right);

    return left;
  };

  private isEmpty(value: unknown): boolean {
    if (value === null) {
      return true;
    }
    if (typeof value === "string") {
      return value.trim() === "";
    }
    if (Array.isArray(value)) {
      return value.length === 0;
    }
    if (value instanceof Set || value instanceof Map) {
      return value.size === 0;
    }
    if (typeof value === "object") {
      return Object.keys(value as Record<string, unknown>).length === 0;
    }
    return false;
  }

  private compareEq(left: unknown, right: unknown): boolean {
    if (Array.isArray(left) && Array.isArray(right)) {
      return isDeepStrictEqual(left, right);
    }
    if (Array.isArray(left)) {
      return left.some((item) => isDeepStrictEqual(item, right));
    }
    if (Array.isArray(right)) {
      return right.some((item) => isDeepStrictEqual(left, item));
    }
    return isDeepStrictEqual(left, right);
  }

  private compareOrder(left: unknown, right: unknown, op: "lt" | "gt" | "lte" | "gte"): boolean {
    if (typeof left === "string" && typeof right === "string") {
      if (op === "lt") return left < right;
      if (op === "gt") return left > right;
      if (op === "lte") return left <= right;
      return left >= right;
    }

    if (op === "lt") return (left as never) < (right as never);
    if (op === "gt") return (left as never) > (right as never);
    if (op === "lte") return (left as never) <= (right as never);
    return (left as never) >= (right as never);
  }

  private checkIn(left: unknown, right: unknown): boolean {
    if (Array.isArray(left)) {
      return left.some((item) => this.checkIn(item, right));
    }
    if (Array.isArray(right)) {
      return right.some((item) => isDeepStrictEqual(item, left));
    }
    if (typeof right === "string") {
      return right.includes(String(left));
    }
    if (right instanceof Set) {
      return right.has(left);
    }
    if (right instanceof Map) {
      return right.has(left);
    }
    if (right && typeof right === "object") {
      return Object.prototype.hasOwnProperty.call(right, String(left));
    }
    return false;
  }

  private contains(haystack: unknown, needle: unknown): boolean {
    if (haystack === null || needle === null) {
      return false;
    }
    if (Array.isArray(haystack)) {
      return haystack.some((item) => this.contains(item, needle));
    }
    return String(haystack).includes(String(needle));
  }

  private startsWith(value: unknown, prefix: unknown): boolean {
    if (value === null || prefix === null) {
      return false;
    }
    if (Array.isArray(value)) {
      return value.some((item) => this.startsWith(item, prefix));
    }
    return String(value).startsWith(String(prefix));
  }

  private endsWith(value: unknown, suffix: unknown): boolean {
    if (value === null || suffix === null) {
      return false;
    }
    if (Array.isArray(value)) {
      return value.some((item) => this.endsWith(item, suffix));
    }
    return String(value).endsWith(String(suffix));
  }

  private matches(value: unknown, pattern: unknown): boolean {
    if (value === null || pattern === null) {
      return false;
    }
    if (Array.isArray(value)) {
      return value.some((item) => this.matches(item, pattern));
    }
    try {
      return new RegExp(String(pattern)).test(String(value));
    } catch {
      return false;
    }
  }

  private containsAny(collection: unknown, values: unknown): boolean {
    if (collection === null || values === null) {
      return false;
    }
    const left = Array.isArray(collection) ? collection : [collection];
    const right = Array.isArray(values) ? values : [values];
    return right.some((value) => left.some((item) => isDeepStrictEqual(item, value)));
  }

  private containsAll(collection: unknown, values: unknown): boolean {
    if (collection === null || values === null) {
      return false;
    }
    const left = Array.isArray(collection) ? collection : [collection];
    const right = Array.isArray(values) ? values : [values];
    return right.every((value) => left.some((item) => isDeepStrictEqual(item, value)));
  }

  public readonly visitNullCoalesce = (ctx: NullCoalesceContext): unknown => {
    const expressions = ctx.addExpr_list();
    let result = this.visitNode(expressions[0]);

    for (let index = 1; index < expressions.length; index += 1) {
      if (result !== null) {
        return result;
      }
      result = this.visitNode(expressions[index]);
    }

    return result;
  };

  public readonly visitAddExpr = (ctx: AddExprContext): unknown => {
    let result = this.visitNode(ctx.mulExpr(0));
    const children = ((ctx as unknown as { children?: unknown[] }).children ?? []) as Array<{ symbol?: Token }>;
    let operatorIndex = 1;

    for (let index = 1; index < ctx.mulExpr_list().length; index += 1) {
      while (operatorIndex < children.length) {
        const symbol = children[operatorIndex]?.symbol;
        if (symbol && [BusinessRulesParser.PLUS, BusinessRulesParser.MINUS].includes(symbol.type)) {
          break;
        }
        operatorIndex += 1;
      }

      const operator = children[operatorIndex]?.symbol;
      operatorIndex += 1;
      const operand = this.visitNode(ctx.mulExpr(index));
      result =
        operator?.type === BusinessRulesParser.PLUS
          ? addValues(result, operand)
          : Number(result) - Number(operand);
    }

    return result;
  };

  public readonly visitMulExpr = (ctx: MulExprContext): unknown => {
    let result = this.visitNode(ctx.unaryExpr(0));
    const children = ((ctx as unknown as { children?: unknown[] }).children ?? []) as Array<{ symbol?: Token }>;
    let operatorIndex = 1;

    for (let index = 1; index < ctx.unaryExpr_list().length; index += 1) {
      while (operatorIndex < children.length) {
        const symbol = children[operatorIndex]?.symbol;
        if (symbol && [BusinessRulesParser.STAR, BusinessRulesParser.SLASH, BusinessRulesParser.MOD].includes(symbol.type)) {
          break;
        }
        operatorIndex += 1;
      }

      const operator = children[operatorIndex]?.symbol;
      operatorIndex += 1;
      const operand = Number(this.visitNode(ctx.unaryExpr(index)));

      if (operator?.type === BusinessRulesParser.STAR) {
        result = Number(result) * operand;
      } else if (operator?.type === BusinessRulesParser.SLASH) {
        result = Number(result) / operand;
      } else {
        result = Number(result) % operand;
      }
    }

    return result;
  };

  public readonly visitUnaryExpr = (ctx: UnaryExprContext): unknown => {
    if (ctx.MINUS()) {
      return -Number(this.visitNode(ctx.unaryExpr()));
    }
    return this.visitNode(ctx.primary());
  };

  public readonly visitPrimary = (ctx: PrimaryContext): unknown => {
    if (ctx.LPAREN()) return this.visitNode(ctx.orExpr());
    if (ctx.literal()) return this.visitNode(ctx.literal());
    if (ctx.functionCall()) return this.visitNode(ctx.functionCall());
    if (ctx.path()) return this.visitNode(ctx.path());
    if (ctx.workflowCall()) return this.visitNode(ctx.workflowCall());
    return null;
  };

  public readonly visitFunctionCall = (ctx: FunctionCallContext): unknown => {
    const functionName = ctx.IDENTIFIER().getText();
    if (!(functionName in BUILTIN_FUNCTIONS)) {
      throw new EvaluationError("", `Unknown function: ${functionName}`);
    }

    const args = ctx.orExpr_list().map((expr: OrExprContext) => this.visitNode(expr));
    try {
      return BUILTIN_FUNCTIONS[functionName](...args);
    } catch (error) {
      throw new EvaluationError(
        "",
        `Error in ${functionName}(): ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  };

  public readonly visitLiteral = (ctx: LiteralContext): unknown => {
    if (ctx.NUMBER()) {
      const text = ctx.NUMBER().getText();
      return text.includes(".") ? Number.parseFloat(text) : Number.parseInt(text, 10);
    }
    if (ctx.STRING()) return unescapeString(ctx.STRING().getText());
    if (ctx.TRUE()) return true;
    if (ctx.FALSE()) return false;
    if (ctx.NONE()) return null;
    if (ctx.list_()) return this.visitNode(ctx.list_());
    return null;
  };

  public readonly visitList_ = (ctx: List_Context): unknown[] =>
    ctx.orExpr_list().map((expr: OrExprContext) => this.visitNode(expr));

  public readonly visitPath = (ctx: PathContext): unknown => {
    const [pathParts, nullSafeIndices] = this.getPathParts(ctx);
    return this.resolver.resolve(pathParts, nullSafeIndices);
  };

  public readonly visitWorkflowCall = (ctx: WorkflowCallContext): unknown => {
    const workflowName = unescapeString(ctx.STRING().getText());
    if (!(workflowName in this.workflows)) {
      throw new WorkflowNotFoundError(workflowName);
    }

    const workflow = this.workflows[workflowName];
    const fn = workflow instanceof Workflow ? workflow.fn : workflow;
    const args = ctx.orExpr_list().map((expr: OrExprContext) => this.visitNode(expr));
    return fn(this.entity, ...args);
  };

  public readonly visitActions = (ctx: ActionsContext): null => {
    for (const action of ctx.action_list()) {
      this.visitNode(action);
      if (this.hasReturned) {
        break;
      }
    }
    return null;
  };

  public readonly visitAction = (ctx: ActionContext): null => {
    if (ctx.returnStmt()) {
      this.visitNode(ctx.returnStmt());
    } else if (ctx.assignment()) {
      this.visitNode(ctx.assignment());
    } else if (ctx.workflowCall()) {
      this.visitNode(ctx.workflowCall());
    }
    return null;
  };

  public readonly visitReturnStmt = (ctx: ReturnStmtContext): never => {
    const value = this.visitNode(ctx.orExpr());
    this.returnValue = value;
    this.hasReturned = true;
    throw new ReturnValue(value);
  };

  public readonly visitAssignment = (ctx: AssignmentContext): null => {
    const [pathParts] = this.getPathParts(ctx.path());
    const value = this.visitNode(ctx.orExpr());
    const assignOp = ctx.assignOp();

    if (assignOp.ASSIGN()) {
      this.resolver.assign(pathParts, value);
      return null;
    }

    const current = this.resolver.resolve(pathParts);
    let newValue = value;

    if (assignOp.PLUS_ASSIGN()) {
      newValue = addValues(current, value);
    } else if (assignOp.MINUS_ASSIGN()) {
      newValue = Number(current) - Number(value);
    } else if (assignOp.STAR_ASSIGN()) {
      newValue = Number(current) * Number(value);
    } else if (assignOp.SLASH_ASSIGN()) {
      newValue = Number(current) / Number(value);
    }

    this.resolver.assign(pathParts, newValue);
    return null;
  };

  private getPathParts(ctx: PathContext): [PathPart[], Set<number>] {
    const parts: PathPart[] = [ctx.IDENTIFIER().getText()];
    const nullSafeIndices = new Set<number>();

    ctx.pathSegment_list().forEach((segment: { NULL_SAFE_DOT(): unknown; IDENTIFIER(): { getText(): string }; DOT(): unknown; LBRACKET(): unknown; orExpr(): OrExprContext }) => {
      if (segment.NULL_SAFE_DOT()) {
        nullSafeIndices.add(parts.length);
        parts.push(segment.IDENTIFIER().getText());
      } else if (segment.DOT()) {
        parts.push(segment.IDENTIFIER().getText());
      } else if (segment.LBRACKET()) {
        const index = this.visitNode(segment.orExpr());
        parts.push(typeof index === "number" ? Math.trunc(index) : String(index));
      }
    });

    return [parts, nullSafeIndices];
  }
}

export function parseRule(ruleText: string, entityName = "entity"): ParsedRule {
  const inputStream = new InputStream(ruleText) as unknown;
  const lexer = new BusinessRulesLexer(inputStream as never);
  const tokenStream = new CommonTokenStream(lexer as never) as unknown;
  const parser = new BusinessRulesParser(tokenStream as never);
  const errorListener = new RuleSyntaxErrorListener(ruleText);

  (parser as unknown as { removeErrorListeners(): void }).removeErrorListeners();
  (parser as unknown as { addErrorListener(listener: object): void }).addErrorListener(errorListener);

  const tree = parser.rule_();
  if (errorListener.errors.length > 0) {
    const [line, column, message] = errorListener.errors[0];
    throw new RuleSyntaxError(ruleText, message, line, column);
  }

  const analyzer = new RuleAnalyzer(entityName);
  analyzer.visitNode(tree);

  return {
    ruleText,
    tree,
    reads: analyzer.reads,
    writes: analyzer.writes,
    workflowCalls: analyzer.workflowCalls,
  };
}
