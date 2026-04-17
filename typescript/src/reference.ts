/**
 * Grammar reference accessor (proposal #7).
 *
 * Rulang ships its canonical grammar reference as inline package data.
 * Consumers that prompt LLMs to write rulang should use `grammarReference()`
 * rather than hand-maintaining a cheatsheet.
 */

import { GRAMMAR_REFERENCE } from "./generated/grammarReference.js";

/**
 * Return the canonical rulang grammar reference as markdown.
 *
 * The reference ships with the package and is versioned alongside it, so
 * pinning rulang pins the reference.
 */
export function grammarReference(): string {
  return GRAMMAR_REFERENCE;
}
