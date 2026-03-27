import { PathResolutionError } from "./errors.js";

type PathPart = string | number;

function entityTypeName(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (value === undefined) {
    return "undefined";
  }
  if (Array.isArray(value)) {
    return "Array";
  }
  if (typeof value === "object") {
    return (value as { constructor?: { name?: string } }).constructor?.name ?? "Object";
  }
  return typeof value;
}

function hasOwnOrInheritedProperty(value: object, key: string): boolean {
  return key in value;
}

function getAttribute(obj: unknown, key: string): unknown {
  if (obj instanceof Map) {
    if (!obj.has(key)) {
      throw new Error(`'Map' has no attribute '${key}'`);
    }
    return obj.get(key);
  }

  if (obj === null || obj === undefined || (typeof obj !== "object" && typeof obj !== "function")) {
    throw new Error(`'${entityTypeName(obj)}' has no attribute '${key}'`);
  }

  if (!hasOwnOrInheritedProperty(obj, key)) {
    throw new Error(`'${entityTypeName(obj)}' has no attribute '${key}'`);
  }

  return (obj as Record<string, unknown>)[key];
}

function normalizeSequenceIndex(length: number, index: number): number {
  return index < 0 ? length + index : index;
}

function getIndex(obj: unknown, index: number): unknown {
  if (obj === null || obj === undefined) {
    throw new Error(`'${entityTypeName(obj)}' does not support indexing`);
  }

  if (typeof obj === "string" || Array.isArray(obj)) {
    const normalizedIndex = normalizeSequenceIndex(obj.length, index);
    if (normalizedIndex < 0 || normalizedIndex >= obj.length) {
      throw new Error(`Index ${index} out of range`);
    }
    return obj[normalizedIndex as keyof typeof obj];
  }

  if (obj instanceof Map) {
    if (!obj.has(index)) {
      throw new Error(`Index ${index} out of range`);
    }
    return obj.get(index);
  }

  if (typeof obj === "object" && index in (obj as { [n: number]: unknown })) {
    return (obj as { [n: number]: unknown })[index];
  }

  throw new Error(`'${entityTypeName(obj)}' does not support indexing`);
}

function setAttribute(obj: unknown, key: string, value: unknown): void {
  if (obj instanceof Map) {
    obj.set(key, value);
    return;
  }

  if (obj === null || obj === undefined || (typeof obj !== "object" && typeof obj !== "function")) {
    throw new Error(`'${entityTypeName(obj)}' has no attribute '${key}'`);
  }

  (obj as Record<string, unknown>)[key] = value;
}

function setIndex(obj: unknown, index: number, value: unknown): void {
  if (obj === null || obj === undefined || typeof (obj as { [n: number]: unknown }) !== "object") {
    throw new Error(`'${entityTypeName(obj)}' does not support index assignment`);
  }

  if (Array.isArray(obj)) {
    const normalizedIndex = normalizeSequenceIndex(obj.length, index);
    if (normalizedIndex < 0 || normalizedIndex >= obj.length) {
      throw new Error(`Index ${index} out of range`);
    }
    obj[normalizedIndex] = value;
    return;
  }

  if (obj instanceof Map) {
    obj.set(index, value);
    return;
  }

  if (!(index in (obj as { [n: number]: unknown }))) {
    throw new Error(`'${entityTypeName(obj)}' does not support index assignment`);
  }

  (obj as { [n: number]: unknown })[index] = value;
}

export class PathResolver {
  public readonly entity: unknown;
  public readonly entityName: string;
  private readonly context: Record<string, unknown>;

  constructor(entity: unknown, entityName = "entity") {
    this.entity = entity;
    this.entityName = entityName;
    this.context = { [entityName]: entity };
  }

  public addToContext(name: string, value: unknown): void {
    this.context[name] = value;
  }

  public normalizePath(pathParts: PathPart[]): PathPart[] {
    if (pathParts.length === 0) {
      return pathParts;
    }

    const [rootName] = pathParts;
    if (typeof rootName === "string" && !(rootName in this.context)) {
      return [this.entityName, ...pathParts];
    }
    return [...pathParts];
  }

  public resolve(pathParts: PathPart[], nullSafeIndices: Set<number> = new Set()): unknown {
    if (pathParts.length === 0) {
      throw new PathResolutionError("", entityTypeName(this.entity), "Empty path");
    }

    const originalLength = pathParts.length;
    const normalized = this.normalizePath(pathParts);
    const shiftedNullSafe =
      normalized.length > originalLength
        ? new Set([...nullSafeIndices].map((index) => index + 1))
        : nullSafeIndices;

    const rootName = normalized[0];
    if (typeof rootName !== "string") {
      throw new PathResolutionError(String(pathParts), entityTypeName(this.entity), "Path must start with an identifier");
    }

    if (!(rootName in this.context)) {
      throw new PathResolutionError(String(pathParts), entityTypeName(this.entity), `Unknown identifier '${rootName}'`);
    }

    let current = this.context[rootName];
    let pathString = rootName;

    for (let offset = 0; offset < normalized.slice(1).length; offset += 1) {
      const part = normalized[offset + 1];
      const segmentIndex = offset + 1;
      const isNullSafe = shiftedNullSafe.has(segmentIndex);

      if (current === null || current === undefined) {
        if (isNullSafe) {
          return null;
        }

        throw new PathResolutionError(pathString, entityTypeName(this.entity), "Cannot access property of None");
      }

      try {
        if (typeof part === "number") {
          pathString += `[${part}]`;
          current = getIndex(current, part);
        } else {
          pathString += `${isNullSafe ? "?." : "."}${part}`;
          current = getAttribute(current, part);
        }
      } catch (error) {
        if (isNullSafe) {
          return null;
        }

        throw new PathResolutionError(
          pathString,
          entityTypeName(this.entity),
          error instanceof Error ? error.message : String(error),
        );
      }
    }

    return current ?? null;
  }

  public resolveForAssignment(pathParts: PathPart[]): [unknown, PathPart] {
    const normalized = this.normalizePath(pathParts);
    if (normalized.length < 2) {
      throw new PathResolutionError(String(pathParts), entityTypeName(this.entity), "Cannot assign to root object");
    }

    return [this.resolve(normalized.slice(0, -1)), normalized[normalized.length - 1]];
  }

  public assign(pathParts: PathPart[], value: unknown): void {
    const [parent, key] = this.resolveForAssignment(pathParts);

    try {
      if (typeof key === "number") {
        setIndex(parent, key, value);
      } else {
        setAttribute(parent, key, value);
      }
    } catch (error) {
      throw new PathResolutionError(
        this.pathToString(pathParts),
        entityTypeName(this.entity),
        error instanceof Error ? error.message : String(error),
      );
    }
  }

  private pathToString(pathParts: PathPart[]): string {
    if (pathParts.length === 0) {
      return "";
    }

    let result = String(pathParts[0]);
    for (const part of pathParts.slice(1)) {
      result += typeof part === "number" ? `[${part}]` : `.${part}`;
    }
    return result;
  }
}
