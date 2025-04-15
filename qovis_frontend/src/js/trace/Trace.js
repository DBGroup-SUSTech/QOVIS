import {TraceTree} from "@/js/trace/TraceTree"
import {QueryPlan} from "@/js/trace/QueryPlan"
// import {TransPath} from "@/js/trace/TransPath"
import {TransLink} from "@/js/trace/TransLink"

export class Trace {
  /** @type {string} */
  name
  /** @type {QueryPlan[]} */
  plans
  /** @type {TraceTree} */
  traceTree
  /** @type {number[][]} */
  costs
  /** @type {TransPath[]} deprecated */
  transforms
  /** @type {Map<number, TransLink[]>} */
  linksMap

  init({name, plans, tree, costs, /*trans,*/ linksMap}) {
    this.name = name
    this.plans = plans.map(p => new QueryPlan().init(p))
    this.traceTree = new TraceTree().init(this, tree)
    this.costs = costs
    this.transforms = []
    // this.transforms = trans.map((trans, idx) => {
    //   const p0 = this.plans[idx], p1 = this.plans[idx + 1]
    //   return new TransPath().init(p0, p1, trans.success, trans.rulePath, trans.links)
    // })
    this.linksMap = new Map()
    this.initLinkForNode(this.traceTree.root, linksMap)
    return this
  }

  /**
   * @param {TraceNode} node
   * @param {{[key: number]: Object[]}} rawMap
   */
  initLinkForNode(node, rawMap) {
    const rawLinks = rawMap[node.id]
    const srcPlan = this.plans[node.startIdx]
    const dstPlan = this.plans[node.endIdx]
    const links = rawLinks.map(link => {
      return new TransLink(
          srcPlan.nodeMap.get(link.vid0),
          dstPlan.nodeMap.get(link.vid1),
          link.kind,
          link.p0,
          link.p1,
          link.idx0,
          link.idx1,
          link.rules)
    })
    this.linksMap.set(node.id, links)

    node.children.forEach(c => this.initLinkForNode(c, rawMap))
  }
}
