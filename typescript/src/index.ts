export { RuleEngine } from "./engine.js";
export { Workflow, workflow, registerWorkflow, getRegisteredWorkflows, clearWorkflowRegistry } from "./workflows.js";
export {
  RuleInterpreterError,
  PathResolutionError,
  RuleSyntaxError,
  CyclicDependencyWarning,
  WorkflowNotFoundError,
  EvaluationError,
} from "./errors.js";
export { parseRule, RuleAnalyzer, RuleInterpreter } from "./visitor.js";
export { DependencyGraph } from "./dependencyGraph.js";
export { PathResolver } from "./pathResolver.js";
export { format, formatAst } from "./formatter.js";
export { grammarReference } from "./reference.js";
export { detectConflicts, type Conflict, type ConflictKind } from "./conflicts.js";
export * as builders from "./builders.js";
export {
  validate,
  BaseResolver,
  OK,
  UNKNOWN,
  DIAGNOSTIC_CODES,
  type Resolver,
  type Diagnostic,
  type PathInfo,
  type Severity,
} from "./validation.js";
export {
  diffEntities,
  type DryRunResult,
  type MatchedRule,
  type ExecutedAction,
  type ActionChange,
  type ActionKind,
} from "./dryRun.js";
export {
  parse,
  walk,
  pathToString,
  ruleLiterals,
  type Span,
  type Rule,
  type Condition,
  type Expr,
  type Action,
  type Path,
  type PathSegment,
  type FieldSegment,
  type NullSafeFieldSegment,
  type IndexSegment,
  type Literal,
  type LiteralType,
  type PathRef,
  type FunctionCall,
  type Binary,
  type BinaryOp,
  type NullCoalesce,
  type Unary,
  type WorkflowCallExpr,
  type Comparison,
  type ComparisonOp,
  type Existence,
  type ExistenceKind,
  type And,
  type Or,
  type Not,
  type SetAction,
  type Compound,
  type CompoundOp,
  type WorkflowCallAction,
  type Return,
} from "./ast.js";
