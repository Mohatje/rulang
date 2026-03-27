#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GRAMMAR_DIR="$ROOT_DIR/grammar"
PYTHON_OUT="$ROOT_DIR/python/src/rulang/grammar/generated"
TYPESCRIPT_OUT="$ROOT_DIR/typescript/src/generated"

mkdir -p "$PYTHON_OUT" "$TYPESCRIPT_OUT"
rm -f "$PYTHON_OUT"/BusinessRules*.py "$PYTHON_OUT"/BusinessRules*.tokens "$PYTHON_OUT"/BusinessRules*.interp
rm -f "$TYPESCRIPT_OUT"/BusinessRules*.ts "$TYPESCRIPT_OUT"/BusinessRules*.tokens "$TYPESCRIPT_OUT"/BusinessRules*.interp

(
  cd "$GRAMMAR_DIR"
  uvx --from antlr4-tools antlr4 -Dlanguage=Python3 -visitor -o "$PYTHON_OUT" BusinessRules.g4
  uvx --from antlr4-tools antlr4 -Dlanguage=TypeScript -visitor -o "$TYPESCRIPT_OUT" BusinessRules.g4
)

for generated_file in "$TYPESCRIPT_OUT"/BusinessRules*.ts; do
  tmp_file="${generated_file}.tmp"
  {
    printf '%s\n' '// @ts-nocheck'
    cat "$generated_file"
  } > "$tmp_file"
  mv "$tmp_file" "$generated_file"
done
