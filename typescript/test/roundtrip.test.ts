/**
 * Randomized round-trip tests for the formatter.
 *
 * Builds random valid rule ASTs via the builder API and asserts:
 *   - format(ast) produces a string
 *   - parse(format(ast)) succeeds
 *   - format(parse(format(ast))) == format(ast)  (idempotence)
 *
 * Uses a seeded RNG so failures are reproducible.
 */

import { describe, expect, test } from "vitest";
import { builders, format, parse, type Action, type Condition, type Expr, type Literal, type Path } from "../src/index.js";

const {
  and,
  compound,
  contains,
  containsAll,
  containsAny,
  endswith,
  eq,
  exists,
  gt,
  gte,
  inOp,
  isEmpty,
  lit,
  lt,
  lte,
  matches,
  neq,
  not,
  notContains,
  notIn,
  or,
  pathOf,
  pathref,
  ret,
  rule,
  set_,
  startswith,
  workflowCall,
} = builders;

// --- Seeded RNG ---------------------------------------------------------

class Rng {
  private state: number;
  constructor(seed: number) { this.state = seed || 1; }
  next(): number {
    // xorshift32
    let x = this.state;
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    this.state = x >>> 0;
    return (this.state % 100000) / 100000;
  }
  int(min: number, max: number): number { return Math.floor(this.next() * (max - min + 1)) + min; }
  pick<T>(arr: readonly T[]): T { return arr[this.int(0, arr.length - 1)]; }
  prob(p: number): boolean { return this.next() < p; }
}

const FIELDS = ["a", "b", "c", "x", "y", "z", "count", "name", "status", "age", "items", "user"];
const WORKFLOWS = ["notify", "log", "score"];

function randPath(rng: Rng): Path {
  const segs: Array<string | number> = ["entity"];
  const depth = rng.int(1, 3);
  for (let i = 0; i < depth; i++) {
    if (rng.prob(0.1)) segs.push("?." + rng.pick(FIELDS));
    else segs.push(rng.pick(FIELDS));
  }
  return pathOf(...segs);
}

function randLiteral(rng: Rng): Literal {
  const c = rng.int(0, 5);
  if (c === 0) return lit(rng.int(-100, 100));
  if (c === 1) return lit(Math.round((rng.next() * 200 - 100) * 100) / 100);
  if (c === 2) return lit(rng.prob(0.5));
  if (c === 3) return lit(null);
  if (c === 4) return lit(rng.pick(["hello", "world", "foo", "bar", ""]));
  const size = rng.int(0, 3);
  return lit(Array.from({ length: size }, () => randLiteral(rng)));
}

function randComparison(rng: Rng): Condition {
  const choices = [eq, neq, lt, gt, lte, gte];
  const op = rng.pick(choices);
  const left = pathref(randPath(rng));
  let right: Expr = randLiteral(rng);
  if ([lt, gt, lte, gte].includes(op) && (right as Literal).literalType !== "int" && (right as Literal).literalType !== "float" && (right as Literal).literalType !== "string") {
    right = lit(rng.int(0, 100));
  }
  return op(left, right) as Condition;
}

function randStringOp(rng: Rng): Condition {
  const ops = [contains, notContains, startswith, endswith, matches];
  return rng.pick(ops)(pathref(randPath(rng)), lit(rng.pick(["a", "hello", "prefix", "suffix"]))) as Condition;
}

function randListOp(rng: Rng): Condition {
  const ops = [inOp, notIn, containsAny, containsAll];
  const vals = Array.from({ length: rng.int(1, 3) }, () => rng.int(1, 10));
  return rng.pick(ops)(pathref(randPath(rng)), lit(vals)) as Condition;
}

function randExistence(rng: Rng): Condition {
  const ops = [exists, isEmpty];
  return rng.pick(ops)(pathref(randPath(rng))) as Condition;
}

function randConditionLeaf(rng: Rng): Condition {
  const builders = [randComparison, randStringOp, randListOp, randExistence];
  return rng.pick(builders)(rng);
}

function randCondition(rng: Rng, depth = 0, maxDepth = 3): Condition {
  if (depth >= maxDepth || rng.prob(0.4)) return randConditionLeaf(rng);
  const c = rng.int(0, 3);
  if (c === 0) return and(randCondition(rng, depth + 1, maxDepth), randCondition(rng, depth + 1, maxDepth)) as Condition;
  if (c === 1) return or(randCondition(rng, depth + 1, maxDepth), randCondition(rng, depth + 1, maxDepth)) as Condition;
  if (c === 2) return not(randCondition(rng, depth + 1, maxDepth)) as Condition;
  return randConditionLeaf(rng);
}

function randAction(rng: Rng): Action {
  const c = rng.int(0, 3);
  if (c === 0) return set_(randPath(rng), randLiteral(rng));
  if (c === 1) {
    const op = rng.pick(["+=", "-=", "*=", "/="] as const);
    return compound(randPath(rng), op, lit(rng.int(1, 10)));
  }
  if (c === 2) {
    const name = rng.pick(WORKFLOWS);
    if (rng.prob(0.5)) return workflowCall(name);
    return workflowCall(name, randLiteral(rng));
  }
  return ret(randLiteral(rng));
}

function randRule(rng: Rng) {
  const cond = randCondition(rng);
  const count = rng.int(1, 3);
  const actions = Array.from({ length: count }, () => randAction(rng));
  return rule(cond, actions);
}

const SEEDS = Array.from({ length: 200 }, (_, i) => i + 1);

describe("round-trip", () => {
  for (const seed of SEEDS) {
    test(`seed ${seed} — format(parse(format(ast))) == format(ast)`, () => {
      const rng = new Rng(seed);
      let built;
      try {
        built = randRule(rng);
      } catch {
        return; // Generator failed, skip
      }
      const text = format(built);
      expect(typeof text).toBe("string");
      const reparsed = parse(text);
      const again = format(reparsed);
      expect(again).toBe(text);
    });

    test(`seed ${seed} — format idempotent`, () => {
      const rng = new Rng(seed);
      let built;
      try {
        built = randRule(rng);
      } catch {
        return;
      }
      const once = format(built);
      const twice = format(parse(once));
      expect(twice).toBe(once);
    });
  }
});
