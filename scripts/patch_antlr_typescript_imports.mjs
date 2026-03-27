import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const outputDir = process.argv[2];

if (!outputDir) {
  throw new Error("Expected the generated TypeScript output directory");
}

const generatedFiles = [
  "BusinessRulesLexer.ts",
  "BusinessRulesParser.ts",
  "BusinessRulesListener.ts",
  "BusinessRulesVisitor.ts",
];

const antlrImportPattern = /import\s*\{([\s\S]*?)\}\s*from\s*["']antlr4["'];/m;

for (const fileName of generatedFiles) {
  const filePath = join(outputDir, fileName);
  const source = readFileSync(filePath, "utf8");
  const match = source.match(antlrImportPattern);

  if (!match) {
    continue;
  }

  const specifiers = match[1]
    .split(",")
    .map((specifier) => specifier.trim())
    .filter(Boolean)
    .join(",\n  ");

  const replacement = `import * as antlr4 from "antlr4";\nconst {\n  ${specifiers}\n} = antlr4;`;
  writeFileSync(filePath, source.replace(match[0], replacement));
}
