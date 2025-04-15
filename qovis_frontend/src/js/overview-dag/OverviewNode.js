export class OverviewNode {
  /** @type {OverviewDag} */
  overviewDag
  /** @type {TraceNode} */
  traceNode

  /** @type {int} */
  x = 0
  /** @type {int} */
  y = 0

  constructor(overviewDag, traceNode) {
    this.overviewDag = overviewDag
    this.traceNode = traceNode
  }

  /**
   * @returns {OverviewEdge[]}
   */
  getInEdges() {
    return this.traceNode.getInEdges().map(e => e.overviewObj)
  }

  /**
   * @returns {OverviewEdge[]}
   */
  getOutEdges() {
    return this.traceNode.getOutEdges().map(e => e.overviewObj)
  }
}
