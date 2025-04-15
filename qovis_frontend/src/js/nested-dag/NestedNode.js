export class NestedNode {
  /** @type {NestedDag} */
  nestedDag
  /** @type {TraceNode} */
  traceNode

  /** @type {int} */
  x = 0
  /** @type {int} */
  y = 0

  constructor(nestedDag, traceNode) {
    this.nestedDag = nestedDag
    this.traceNode = traceNode
  }

  /**
   * @returns {NestedEdge[]}
   */
  getInEdges() {
    return this.traceNode.getInEdges().map(e => e.nestedObj)
  }

  /**
   * @returns {NestedEdge[]}
   */
  getOutEdges() {
    return this.traceNode.getOutEdges().map(e => e.nestedObj)
  }
}
