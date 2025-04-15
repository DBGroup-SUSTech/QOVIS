import {OverviewEdge} from "@/js/overview-dag/OverviewEdge"
import {NestedEdge} from "@/js/nested-dag/NestedEdge"

export class TraceEdge {
  /** @type {TraceDag} */
  traceDag

  /** @type {String} */
  eid
  /** @type {int} */
  src
  /** @type {int} */
  dst
  /** @type {Object} */
  meta

  /** @type {OverviewEdge} */
  overviewObj
  /** @type {NestedEdge} */
  nestedObj

  constructor(traceDag) {
    this.traceDag = traceDag
  }

  createOverviewObj(overviewDag) {
    const obj = new OverviewEdge(overviewDag, this)
    this.overviewObj = obj
    return obj
  }

  createNestedObj(nestedDag) {
    const obj = new NestedEdge(nestedDag, this)
    this.nestedObj = obj
    return obj
  }

  getSrc() {
    return this.traceDag.nodeMap.get(this.src)
  }

  getDst() {
    return this.traceDag.nodeMap.get(this.dst)
  }
}
