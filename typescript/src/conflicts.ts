/**
 * Conflict detection (proposal #5).
 *
 * Mirrors `rulang/conflicts.py`. Uses the public `format*` helpers so
 * canonical-form comparison is exact; no string-splitting on format() output.
 */

import {
  parse,
  type Rule,
  type SetAction,
  type Compound,
  type Literal,
} from "./ast.js";
import { formatAction, formatCondition, formatPath } from "./formatter.js";

export type ConflictKind = "duplicate" | "contradiction" | "shadowing";

export interface Conflict {
  readonly kind: ConflictKind;
  readonly ruleIndices: readonly [number, number];
  readonly fields: readonly string[];
  readonly diff: Record<string, [unknown, unknown]>;
  readonly message: string;
}

export type EvaluationMode = "first_match" | "all_match";

export function detectConflicts(
  rules: Array<string | Rule>,
  options: { mode?: EvaluationMode; entityName?: string } = {},
): Conflict[] {
  const { mode = "all_match", entityName = "entity" } = options;
  const asts: Rule[] = rules.map((r) => (typeof r === "string" ? parse(r, entityName) : r));
  const metas = asts.map(analyze);

  const conflicts: Conflict[] = [];
  for (let i = 0; i < asts.length; i++) {
    for (let j = i + 1; j < asts.length; j++) {
      const m1 = metas[i];
      const m2 = metas[j];
      if (m1.conditionCanon !== m2.conditionCanon) continue;

      if (setEquals(m1.actionsCanon, m2.actionsCanon)) {
        conflicts.push({
          kind: "duplicate",
          ruleIndices: [i, j],
          fields: [...m1.writePaths].sort(),
          diff: {},
          message: `Rules ${i} and ${j} are identical after normalization.`,
        });
        continue;
      }

      const sharedLiteralPaths = new Set<string>();
      for (const path of m1.literalWrites.keys()) {
        if (m2.literalWrites.has(path)) sharedLiteralPaths.add(path);
      }
      const diffFields: string[] = [];
      for (const path of sharedLiteralPaths) {
        const a = m1.literalWrites.get(path)!;
        const b = m2.literalWrites.get(path)!;
        if (!valueEquals(a, b)) diffFields.push(path);
      }

      if (diffFields.length > 0) {
        diffFields.sort();
        const diff: Record<string, [unknown, unknown]> = {};
        for (const f of diffFields) {
          diff[f] = [m1.literalWrites.get(f)!, m2.literalWrites.get(f)!];
        }
        conflicts.push({
          kind: "contradiction",
          ruleIndices: [i, j],
          fields: diffFields,
          diff,
          message:
            `Rules ${i} and ${j} have identical conditions but write different literal values to: ` +
            diffFields.join(", ") +
            ".",
        });
        continue;
      }

      if (mode === "first_match") {
        conflicts.push({
          kind: "shadowing",
          ruleIndices: [i, j],
          fields: [],
          diff: {},
          message:
            `Rule ${j} is unreachable in first_match mode: rule ${i} has an identical condition and runs first.`,
        });
      }
    }
  }

  return conflicts;
}

interface RuleMeta {
  readonly conditionCanon: string;
  readonly actionsCanon: Set<string>;
  readonly writePaths: Set<string>;
  /** Map of write-path → tagged literal (type + value), used for contradiction check. */
  readonly literalWrites: Map<string, [string, unknown]>;
}

function analyze(rule: Rule): RuleMeta {
  const conditionCanon = formatCondition(rule.condition);
  const actionsCanon = new Set<string>(rule.actions.map(formatAction));

  const writePaths = new Set<string>();
  const literalWrites = new Map<string, [string, unknown]>();
  for (const action of rule.actions) {
    if (action.type === "set" || action.type === "compound") {
      const path = formatPath((action as SetAction | Compound).path);
      writePaths.add(path);
      if (action.type === "set" && (action as SetAction).value.type === "literal") {
        const lit = (action as SetAction).value as Literal;
        literalWrites.set(path, [lit.literalType, lit.value]);
      }
    }
  }

  return { conditionCanon, actionsCanon, writePaths, literalWrites };
}

function setEquals<T>(a: Set<T>, b: Set<T>): boolean {
  if (a.size !== b.size) return false;
  for (const x of a) if (!b.has(x)) return false;
  return true;
}

function valueEquals(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!valueEquals(a[i], b[i])) return false;
    }
    return true;
  }
  return false;
}
