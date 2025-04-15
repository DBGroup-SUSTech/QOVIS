import {VisTraceTree} from "@/js/trace/VisTraceTree"
import {VisTraceNode} from "@/js/trace/VisTraceNode"


/**
 * @enum {string}
 * @readonly
 */
export const ProcType = {
  ROOT: 'root',
  PHASE: 'phase',
  BATCH: 'batch',
  RULE: 'rule',
  OTHER: 'other',
  GROUP: 'group'
}

export class TraceTree {
  /** @type {Trace} */
  trace
  /** @type {TraceNode} */
  root = new TraceNode()
  /** @type {number} */
  maxFirstLevelStepCnt = 0

  /** @type {VisTraceTree} */
  visObj = null

  init(trace, raw) {
    this.trace = trace
    this.root.init(this, null, raw)
    this.maxFirstLevelStepCnt = this.root.children
        .reduce((acc, cur) => Math.max(acc, cur.ruleStepCnt), 0)
    return this
  }

  createVisObj() {
    this.visObj = new VisTraceTree(this)
    return this.visObj
  }
}

export class TraceNode {
  /** @type {number} */
  id
  /** @type {TraceTree} */
  traceTree
  /** @type {TraceNode} */
  parent = null
  /** @type {TraceNode[]} */
  children = []
  /** @type {string} */
  name
  /** @type {ProcType} */
  type
  // the plan slice [startIdx, endIdx]
  /** @type {number} */
  startIdx = 0
  /** @type {number} */
  endIdx = 0
  /** @type {object[]} */
  events

  /** @type {VisTraceNode} */
  visObj = null

  /**
   * @param {TraceTree} traceTree
   * @param {TraceNode} parent
   * @param {number} id
   * @param {string} name
   * @param {ProcType} type
   * @param {number} startIdx
   * @param {number} endIdx
   * @param {object[]} events
   * @param {object[]} children
   *
   * @returns {this}
   */
  init(traceTree, parent, {id, name, type, startIdx, endIdx, events, children}) {
    this.traceTree = traceTree
    this.parent = parent
    this.id = id
    this.name = name
    this.type = type
    this.startIdx = startIdx
    this.endIdx = endIdx
    this.events = events

    this.children = children.map(c => new TraceNode().init(traceTree, this, c))

    return this
  }

  createVisObj() {
    this.visObj = new VisTraceNode()
    this.visObj.origin = this
    return this.visObj
  }

  get isRoot() {
    return this.type === ProcType.ROOT
  }

  getSimpleName() {
    let name = this.name
    if (!name || name === '') {
      name = 'Unknown'
    }
    if (name.endsWith("$")) {
      name = name.substring(0, name.length - 1)
    }
    if (name.includes('.')) {
      name = name.split('.').at(-1)
    }
    if (name.includes("$")) {
      name = name.split("$")[1]
    }
    return name
  }

  get ruleStepCnt() {
    return this.endIdx - this.startIdx + 1
  }

  // getSimpleNameWithCnt() {
  //   let name = this.getSimpleName()
  //   if (this.isPatternNode() && this.children.length > 1) {
  //     name += ` (${this.children.length})`
  //   }
  //   return name
  // }
}

