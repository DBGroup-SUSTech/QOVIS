import {Plan} from "@/js/plan/Plan"

export class DynamicGraph {
  /** @type {string} */
  queryName
  /** @type {Plan[]} */
  plans
  /** @type {[int, int][]} */
  phaseIntervals
  /** @type {string[]} */
  phaseNames

  static load(dg) {
    const ret = new DynamicGraph()
    ret.queryName = dg.queryName
    ret.plans = dg.plans.map(p => Plan.load(p))
    ret.phaseIntervals = dg.phaseIntervals
    ret.phaseNames = dg.phaseNames
    return ret
  }
}
