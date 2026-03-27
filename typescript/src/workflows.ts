export type WorkflowFunction = (entity: unknown, ...args: unknown[]) => unknown;

export class Workflow {
  public readonly fn: WorkflowFunction;
  public readonly reads: string[];
  public readonly writes: string[];

  constructor(options: {
    fn: WorkflowFunction;
    reads?: string[];
    writes?: string[];
  }) {
    this.fn = options.fn;
    this.reads = options.reads ?? [];
    this.writes = options.writes ?? [];
  }

  public call(entity: unknown, ...args: unknown[]): unknown {
    return this.fn(entity, ...args);
  }
}

export type WorkflowLike = Workflow | WorkflowFunction;
export type WorkflowRegistry = Record<string, WorkflowLike>;

const workflowRegistry: WorkflowRegistry = {};

export function workflow(
  name: string,
  options: {
    reads?: string[];
    writes?: string[];
    fn: WorkflowFunction;
  },
): WorkflowFunction {
  workflowRegistry[name] = new Workflow(options);
  return options.fn;
}

export function registerWorkflow(
  name: string,
  fn: WorkflowFunction,
  reads?: string[],
  writes?: string[],
): WorkflowFunction {
  return workflow(name, { fn, reads, writes });
}

export function getRegisteredWorkflows(): WorkflowRegistry {
  return { ...workflowRegistry };
}

export function clearWorkflowRegistry(): void {
  for (const name of Object.keys(workflowRegistry)) {
    delete workflowRegistry[name];
  }
}

export function mergeWorkflows(
  passedWorkflows?: WorkflowRegistry,
): WorkflowRegistry {
  return {
    ...getRegisteredWorkflows(),
    ...(passedWorkflows ?? {}),
  };
}
