import { CyclicDependencyWarning } from "./errors.js";
import type { ParsedRule } from "./visitor.js";
import type { WorkflowLike } from "./workflows.js";

export interface RuleNode {
  index: number;
  rule: ParsedRule;
  reads: Set<string>;
  writes: Set<string>;
}

function cloneGraph(graph: Map<number, Set<number>>): Record<number, Set<number>> {
  return Object.fromEntries(
    [...graph.entries()].map(([key, value]) => [key, new Set(value)]),
  );
}

export class DependencyGraph {
  public readonly nodes: RuleNode[] = [];
  private readonly edges = new Map<number, Set<number>>();
  private readonly reverseEdges = new Map<number, Set<number>>();
  private analyzed = false;

  public addRule(rule: ParsedRule, workflows?: Record<string, WorkflowLike>): number {
    const index = this.nodes.length;
    const reads = new Set(rule.reads);
    const writes = new Set(rule.writes);

    if (workflows) {
      for (const workflowName of rule.workflowCalls) {
        const workflow = workflows[workflowName];
        if (!workflow || typeof workflow === "function") {
          continue;
        }

        workflow.reads.forEach((path) => reads.add(path));
        workflow.writes.forEach((path) => writes.add(path));
      }
    }

    this.nodes.push({ index, rule, reads, writes });
    this.analyzed = false;
    return index;
  }

  public analyze(): void {
    if (this.analyzed) {
      return;
    }

    this.edges.clear();
    this.reverseEdges.clear();

    this.nodes.forEach((nodeA, i) => {
      this.nodes.forEach((nodeB, j) => {
        if (i === j) {
          return;
        }

        if (this.pathsOverlap(nodeB.reads, nodeA.writes)) {
          if (!this.edges.has(i)) {
            this.edges.set(i, new Set());
          }
          if (!this.reverseEdges.has(j)) {
            this.reverseEdges.set(j, new Set());
          }
          this.edges.get(i)!.add(j);
          this.reverseEdges.get(j)!.add(i);
        }
      });
    });

    this.analyzed = true;
  }

  private pathsOverlap(reads: Set<string>, writes: Set<string>): boolean {
    for (const readPath of reads) {
      for (const writePath of writes) {
        if (this.pathMatches(readPath, writePath)) {
          return true;
        }
      }
    }
    return false;
  }

  private pathMatches(path1: string, path2: string): boolean {
    const parts1 = path1.replaceAll("[*]", ".[*]").split(".");
    const parts2 = path2.replaceAll("[*]", ".[*]").split(".");
    const minLength = Math.min(parts1.length, parts2.length);

    for (let index = 0; index < minLength; index += 1) {
      const left = parts1[index];
      const right = parts2[index];

      if (left === "[*]" || right === "[*]") {
        continue;
      }

      if (left !== right) {
        return false;
      }
    }

    return true;
  }

  public detectCycles(): number[][] {
    this.analyze();

    const cycles: number[][] = [];
    const visited = new Set<number>();
    const recStack = new Set<number>();

    const dfs = (node: number, path: number[]) => {
      visited.add(node);
      recStack.add(node);
      path.push(node);

      for (const neighbor of this.edges.get(node) ?? []) {
        if (!visited.has(neighbor)) {
          dfs(neighbor, path);
        } else if (recStack.has(neighbor)) {
          const cycleStart = path.indexOf(neighbor);
          cycles.push([...path.slice(cycleStart), neighbor]);
        }
      }

      path.pop();
      recStack.delete(node);
    };

    this.nodes.forEach((_, index) => {
      if (!visited.has(index)) {
        dfs(index, []);
      }
    });

    return cycles;
  }

  public getExecutionOrder(): number[] {
    this.analyze();
    const cycles = this.detectCycles();

    if (cycles.length > 0) {
      this.breakCycles(cycles);
    }

    const inDegree = new Map<number, number>();
    this.nodes.forEach((_, index) => inDegree.set(index, 0));
    this.edges.forEach((targets) => {
      targets.forEach((target) => {
        inDegree.set(target, (inDegree.get(target) ?? 0) + 1);
      });
    });

    const queue = [...inDegree.entries()]
      .filter(([, degree]) => degree === 0)
      .map(([index]) => index);
    const result: number[] = [];

    while (queue.length > 0) {
      queue.sort((left, right) => left - right);
      const node = queue.shift()!;
      result.push(node);

      for (const neighbor of this.edges.get(node) ?? []) {
        const next = (inDegree.get(neighbor) ?? 0) - 1;
        inDegree.set(neighbor, next);
        if (next === 0) {
          queue.push(neighbor);
        }
      }
    }

    if (result.length !== this.nodes.length) {
      const remaining = this.nodes
        .map((_, index) => index)
        .filter((index) => !result.includes(index));
      result.push(...remaining.sort((left, right) => left - right));
    }

    return result;
  }

  private breakCycles(cycles: number[][]): void {
    for (const cycle of cycles) {
      const cycleNodes = cycle[0] === cycle[cycle.length - 1] ? cycle.slice(0, -1) : cycle;
      const minNode = Math.min(...cycleNodes);

      for (let index = 0; index < cycleNodes.length; index += 1) {
        const node = cycleNodes[index];
        const nextNode = cycleNodes[(index + 1) % cycleNodes.length];

        if (nextNode === minNode && this.edges.get(node)?.has(minNode)) {
          process.emitWarning(new CyclicDependencyWarning(cycle));
          this.edges.get(node)?.delete(minNode);
          this.reverseEdges.get(minNode)?.delete(node);
          break;
        }
      }
    }
  }

  public getDependencies(ruleIndex: number): Set<number> {
    this.analyze();
    return new Set(this.reverseEdges.get(ruleIndex) ?? []);
  }

  public getDependents(ruleIndex: number): Set<number> {
    this.analyze();
    return new Set(this.edges.get(ruleIndex) ?? []);
  }

  public getGraph(): Record<number, Set<number>> {
    this.analyze();
    return cloneGraph(this.edges);
  }

  public get size(): number {
    return this.nodes.length;
  }
}
