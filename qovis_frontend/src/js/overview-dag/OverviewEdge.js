export class OverviewEdge {
  /** @type {OverviewDag} */
  overviewDag
  /** @type {TraceEdge} */
  traceEdge

  constructor(overviewDag, traceEdge) {
    this.overviewDag = overviewDag
    this.traceEdge = traceEdge
  }

  /**
   * @returns {OverviewNode}
   */
  getSrc() {
    return this.traceEdge.getSrc().overviewObj
  }

  /**
   * @returns {OverviewNode}
   */
  getDst() {
    return this.traceEdge.getDst().overviewObj
  }
}
