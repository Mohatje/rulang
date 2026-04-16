import { describe, expect, test } from "vitest";
import {
  BaseResolver,
  OK,
  UNKNOWN,
  parse,
  validate,
  type Diagnostic,
  type Expr,
  type Literal,
  type Path,
  type PathInfo,
} from "../src/index.js";

describe("never raises, empty by default", () => {
  test("BaseResolver emits nothing", () => {
    expect(validate("entity.x == 1 => entity.y = 2", new BaseResolver())).toEqual([]);
  });
});

describe("parse errors become diagnostics", () => {
  test("syntax_error diagnostic", () => {
    const result = validate("entity.x ===", new BaseResolver());
    expect(result).toHaveLength(1);
    expect(result[0].code).toBe("rulang.syntax_error");
    expect(result[0].severity).toBe("error");
  });

  test("parse failure stops further validation", () => {
    const result = validate("entity.x ===", new BaseResolver());
    expect(result.every((d) => d.code === "rulang.syntax_error")).toBe(true);
  });
});

describe("check_path", () => {
  class UnknownPath extends BaseResolver {
    override checkPath(_path: Path): PathInfo {
      return { exists: false };
    }
  }

  class ReadOnly extends BaseResolver {
    override checkPath(_path: Path): PathInfo {
      return { exists: true, writable: false };
    }
  }

  test("unknown path emits diagnostic", () => {
    const result = validate("entity.missing == 1 => entity.y = 2", new UnknownPath());
    expect(result.some((d) => d.code === "rulang.unknown_path")).toBe(true);
  });

  test("non-writable emits distinct code", () => {
    const result = validate("entity.x == 1 => entity.y = 2", new ReadOnly());
    expect(result.some((d) => d.code === "rulang.path_not_writable")).toBe(true);
  });

  test("good paths produce nothing", () => {
    class AllFine extends BaseResolver {
      override checkPath(): PathInfo {
        return { exists: true, writable: true };
      }
    }
    expect(validate("entity.x == 1 => entity.y = 2", new AllFine())).toEqual([]);
  });
});

describe("check_assignment / consumer diagnostics", () => {
  class BanHigh extends BaseResolver {
    override checkAssignment(_path: Path, value: Expr): Diagnostic[] | typeof OK {
      if (value.type === "literal" && (value as Literal).value === "high") {
        return [{ code: "myapp.no_high", message: "no high allowed", severity: "error" }];
      }
      return OK;
    }
  }

  test("consumer diagnostic surfaces", () => {
    const result = validate("entity.x == 1 => entity.priority = 'high'", new BanHigh());
    expect(result).toHaveLength(1);
    expect(result[0].code).toBe("myapp.no_high");
  });

  test("default OK produces nothing", () => {
    expect(validate("entity.x == 1 => entity.priority = 'high'", new BaseResolver())).toEqual([]);
  });
});

describe("check_comparison", () => {
  class NoStringComp extends BaseResolver {
    override checkComparison(left: Expr, _op: string, right: Expr): Diagnostic[] | typeof OK {
      const isStringLit = (e: Expr) => e.type === "literal" && (e as Literal).literalType === "string";
      if (isStringLit(left) || isStringLit(right)) {
        return [{ code: "myapp.no_string_comp", message: "no string comparisons", severity: "error" }];
      }
      return OK;
    }
  }

  test("flags string comparisons", () => {
    const result = validate("entity.x == 'foo' => entity.y = 1", new NoStringComp());
    expect(result.some((d) => d.code === "myapp.no_string_comp")).toBe(true);
  });
});

describe("check_workflow_call", () => {
  class NoWorkflows extends BaseResolver {
    override checkWorkflowCall(name: string): Diagnostic[] {
      return [{ code: "rulang.unknown_workflow", message: `unknown workflow: ${name}`, severity: "error" }];
    }
  }

  test("action position", () => {
    const result = validate('entity.x == 1 => workflow("notify")', new NoWorkflows());
    expect(result.some((d) => d.code === "rulang.unknown_workflow")).toBe(true);
  });

  test("expression position", () => {
    const result = validate('workflow("fetch") == true => entity.y = 1', new NoWorkflows());
    expect(result.some((d) => d.code === "rulang.unknown_workflow")).toBe(true);
  });
});

describe("sentinels", () => {
  class UnknownAll extends BaseResolver {
    override checkPath(): typeof UNKNOWN { return UNKNOWN; }
  }

  test("UNKNOWN produces no diagnostics", () => {
    expect(validate("entity.x == 1 => entity.y = 2", new UnknownAll())).toEqual([]);
  });
});

describe("severity overrides", () => {
  class UnknownPath extends BaseResolver {
    override checkPath(): PathInfo { return { exists: false }; }
  }

  test("downgrade rulang code", () => {
    const result = validate(
      "entity.missing == 1 => entity.y = 2",
      new UnknownPath(),
      { severityOverrides: { "rulang.unknown_path": "warning" } },
    );
    const unknown = result.filter((d) => d.code === "rulang.unknown_path");
    for (const d of unknown) expect(d.severity).toBe("warning");
  });

  test("apply to consumer code", () => {
    class BanHigh extends BaseResolver {
      override checkAssignment(_path: Path, value: Expr): Diagnostic[] | typeof OK {
        if (value.type === "literal" && (value as Literal).value === "high") {
          return [{ code: "myapp.no_high", message: "no high", severity: "error" }];
        }
        return OK;
      }
    }
    const result = validate(
      "entity.x == 1 => entity.priority = 'high'",
      new BanHigh(),
      { severityOverrides: { "myapp.no_high": "info" } },
    );
    expect(result[0].severity).toBe("info");
  });
});

describe("accepts AST input", () => {
  test("Rule passed directly", () => {
    const rule = parse("entity.x == 1 => entity.y = 2");
    expect(validate(rule, new BaseResolver())).toEqual([]);
  });
});

describe("spans on diagnostics", () => {
  class UnknownPath extends BaseResolver {
    override checkPath(): PathInfo { return { exists: false }; }
  }

  test("unknown_path carries span", () => {
    const result = validate("entity.missing == 1 => entity.y = 2", new UnknownPath());
    const d = result.find((x) => x.code === "rulang.unknown_path");
    expect(d?.span).toBeDefined();
    expect(d?.span?.start).toBeGreaterThanOrEqual(0);
  });
});

describe("walks into list literals and indices", () => {
  class UnknownPath extends BaseResolver {
    override checkPath(): PathInfo { return { exists: false }; }
  }

  test("list literal element", () => {
    const result = validate("entity.x in [entity.missing] => entity.y = 1", new UnknownPath());
    expect(result.filter((d) => d.code === "rulang.unknown_path").length).toBeGreaterThan(0);
  });

  test("index expression", () => {
    const result = validate("entity.items[entity.missing].name == 'x' => entity.y = 1", new UnknownPath());
    expect(result.filter((d) => d.code === "rulang.unknown_path").length).toBeGreaterThan(0);
  });
});
