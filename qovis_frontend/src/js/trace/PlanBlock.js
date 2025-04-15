export class PlanBlock {
  /** @type {VisTraceTree} */
  visTraceTree
  /** @type {VisTraceNode} */
  parentVisNode
  /** @type {number} */
  idx   // the position this plan located. 0 means the first plan in the front of the trace node (action)
  /** @type {VisQueryPlan} */
  visPlan

  centerX = 0
  topY = 0    // the top of the rect part
  // width = 0
  // height = 0
  radius = 0  // the radius of the circle part above and below the rect
  rectHeight = 0    // the height of the rect part

  /**
   * @param {VisTraceTree} visTraceTree
   * @param {VisTraceNode} parentVisNode
   * @param {number} idx the position this plan located. 0 means the first plan in the front of the trace node (action)
   * @param {VisQueryPlan} visPlan
   */
  constructor(visTraceTree, parentVisNode, idx, visPlan) {
    this.visTraceTree = visTraceTree
    this.parentVisNode = parentVisNode
    this.visPlan = visPlan
    this.idx = idx
  }

  get level() {
    return this.parentVisNode.level + 1
  }
}
