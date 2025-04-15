export class NestedEdge {
  /** @type {NestedDag} */
  nestedDag
  /** @type {TraceEdge} */
  traceEdge

  constructor(nestedDag, traceEdge) {
    this.nestedDag = nestedDag
    this.traceEdge = traceEdge
  }

  /**
   * @returns {NestedNode}
   */
  getSrc() {
    return this.traceEdge.getSrc().nestedObj
  }

  /**
   * @returns {NestedNode}
   */
  getDst() {
    return this.traceEdge.getDst().nestedObj
  }
}
