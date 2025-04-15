import {OverviewNode} from "@/js/overview-dag/OverviewNode"
import {NestedNode} from "@/js/nested-dag/NestedNode"

export class TraceNode {
  /** @type {TraceDag} */
  traceDag

  /** @type {int} */
  nid
  /** @type {String[]} */
  inEdges
  /** @type {String[]} */
  outEdges
  /** @type {Object} */
  meta

  /** @type {int} */
  rank

  /** @type {OverviewNode} */
  overviewObj
  /** @type {NestedNode} */
  nestedObj

  constructor(traceDag) {
    this.traceDag = traceDag
  }

  createOverviewObj(overviewDag) {
    const obj = new OverviewNode(overviewDag, this)
    this.overviewObj = obj
    return obj
  }

  createNestedObj(nestedDag) {
    const obj = new NestedNode(nestedDag, this)
    this.nestedObj = obj
    return obj
  }

  /**
   * @param index
   * @returns {TraceEdge}
   */
  getInEdge(index) {
    return this.traceDag.edgeMap.get(this.inEdges[index])
  }

  /**
   * @param index
   * @returns {TraceEdge}
   */
  getOutEdge(index) {
    return this.traceDag.edgeMap.get(this.outEdges[index])
  }

  /**
   * @returns {TraceEdge[]}
   */
  getInEdges() {
    return this.inEdges.map(eid => this.traceDag.edgeMap.get(eid))
  }

  /**
   * @returns {TraceEdge[]}
   */
  getOutEdges() {
    return this.outEdges.map(eid => this.traceDag.edgeMap.get(eid))
  }
}
