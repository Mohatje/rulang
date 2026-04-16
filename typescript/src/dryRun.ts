/**
 * Dry-run diff API (proposal #8).
 *
 * Mirrors `rulang/dry_run.py`. Engine.dryRun() returns a DryRunResult with a
 * structured trace of what matched, what executed, and per-action diffs.
 */

export type ActionKind = "set" | "compound" | "workflow" | "return";

export interface MatchedRule {
  readonly index: number;
  readonly ruleText: string;
  readonly conditionResult: boolean;
  readonly executed: boolean;
}

export interface ActionChange {
  readonly path: string;
  readonly before: unknown;
  readonly after: unknown;
}

export interface ExecutedAction {
  readonly ruleIndex: number;
  readonly actionKind: ActionKind;
  readonly changes: readonly ActionChange[];
  readonly returned?: unknown;
}

export interface DryRunResult {
  readonly matchedRules: readonly MatchedRule[];
  readonly executedActions: readonly ExecutedAction[];
  readonly diff: Record<string, [unknown, unknown]>;
  readonly finalEntity: unknown;
  readonly returned: unknown;
  readonly anyMatched: boolean;
}

// --- Entity diff --------------------------------------------------------

function sameValue(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (a === null || b === null) return false;
  if (typeof a !== typeof b) return false;
  if (typeof a !== "object") return false;
  // Arrays
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!sameValue(a[i], b[i])) return false;
    }
    return true;
  }
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  // Plain objects
  const ak = Object.keys(a as object);
  const bk = Object.keys(b as object);
  if (ak.length !== bk.length) return false;
  for (const k of ak) {
    if (!(k in (b as Record<string, unknown>))) return false;
    if (!sameValue((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k])) return false;
  }
  return true;
}

export function diffEntities(
  before: unknown,
  after: unknown,
  path = "",
): Record<string, [unknown, unknown]> {
  if (sameValue(before, after)) return {};

  const typeMismatch =
    typeof before !== typeof after ||
    Array.isArray(before) !== Array.isArray(after) ||
    before === null ||
    after === null;
  if (typeMismatch) {
    return { [path || "<root>"]: [before, after] };
  }

  if (Array.isArray(before) && Array.isArray(after)) {
    if (before.length !== after.length) {
      return { [path || "<root>"]: [before, after] };
    }
    const changes: Record<string, [unknown, unknown]> = {};
    for (let i = 0; i < before.length; i++) {
      Object.assign(changes, diffEntities(before[i], after[i], `${path}[${i}]`));
    }
    return changes;
  }

  if (typeof before === "object" && before !== null && after !== null) {
    const b = before as Record<string, unknown>;
    const a = after as Record<string, unknown>;
    const keys = new Set([...Object.keys(b), ...Object.keys(a)]);
    const changes: Record<string, [unknown, unknown]> = {};
    for (const k of keys) {
      const subPath = path ? `${path}.${k}` : k;
      const bv = k in b ? b[k] : undefined;
      const av = k in a ? a[k] : undefined;
      if (!(k in b)) changes[subPath] = [null, av];
      else if (!(k in a)) changes[subPath] = [bv, null];
      else Object.assign(changes, diffEntities(bv, av, subPath));
    }
    return changes;
  }

  return { [path || "<root>"]: [before, after] };
}

export function mergeIntoAggregate(
  aggregate: Record<string, [unknown, unknown]>,
  path: string,
  before: unknown,
  after: unknown,
): void {
  if (path in aggregate) {
    const originalBefore = aggregate[path][0];
    if (sameValue(originalBefore, after)) {
      delete aggregate[path];
    } else {
      aggregate[path] = [originalBefore, after];
    }
  } else {
    aggregate[path] = [before, after];
  }
}

export function deepCopy<T>(value: T): T {
  if (value === null || typeof value !== "object") return value;
  if (Array.isArray(value)) return value.map((v) => deepCopy(v)) as unknown as T;
  if (value instanceof Date) return new Date(value.getTime()) as unknown as T;
  if (value instanceof Map) {
    const out = new Map();
    for (const [k, v] of value.entries()) out.set(deepCopy(k), deepCopy(v));
    return out as unknown as T;
  }
  if (value instanceof Set) {
    return new Set([...value].map((v) => deepCopy(v))) as unknown as T;
  }
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(value as object)) out[k] = deepCopy(v);
  return out as T;
}
