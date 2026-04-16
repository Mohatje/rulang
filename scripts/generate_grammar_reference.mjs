#!/usr/bin/env node
/**
 * Syncs docs/grammar-reference.md into:
 *   - python/src/rulang/docs/grammar-reference.md   (package data)
 *   - typescript/src/generated/grammarReference.ts  (inline string export)
 *
 * Run this whenever docs/grammar-reference.md changes so both runtimes stay
 * in lockstep.
 */
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const source = resolve(root, "docs/grammar-reference.md");
const pyDest = resolve(root, "python/src/rulang/docs/grammar-reference.md");
const tsDest = resolve(root, "typescript/src/generated/grammarReference.ts");

const content = await readFile(source, "utf-8");

await mkdir(dirname(pyDest), { recursive: true });
await writeFile(pyDest, content, "utf-8");

const tsBody = `// Generated from docs/grammar-reference.md — do not edit by hand.
// Run scripts/generate_grammar_reference.mjs to regenerate.

export const GRAMMAR_REFERENCE = ${JSON.stringify(content)};
`;
await mkdir(dirname(tsDest), { recursive: true });
await writeFile(tsDest, tsBody, "utf-8");

console.log(`Synced grammar reference:\n  → ${pyDest}\n  → ${tsDest}`);
