import {ProcType} from "@/js/trace/TraceTree"

export class VisTraceNode {
  /** @type {VisTraceNode} */
  parent = null
  /** @type {VisTraceNode[]} */
  children = []

  /** @type {TraceNode} */
  origin

  /** @type {number} */
  level

  // layout of corresponding rectangle
  x = 0       // the center X of last plan block
  y = 0       // the center Y of the transform link visualization
  width = 0   // distance of center X between two plan blocks
  lineHeight = 0

  color = '#000000'

  // interaction
  expanded = false
  maxExpandedLevel = 0    // max of level of expanded children

  /**
   * @param {VisTraceNode} parent
   *
   * @returns {VisTraceNode}
   */
  init(parent) {
    this.parent = parent
    this.children = []
    this.children = this.origin.children.map(child => child.createVisObj().init(this))
    return this
  }

  setExpanded(expanded) {
    this.expanded = expanded
    // if (expanded) {
    //   this.propagateExpanded()
    // } else {
    //   this.maxExpandedLevel = this.level
    //   this.parent.propagateExpanded()
    // }
  }

  propagateExpanded() {
    this.maxExpandedLevel = this.children
        .map(c => c.expanded ? c.maxExpandedLevel + 1 : this.level)
        .reduce((acc, cur) => Math.max(acc, cur), 0)
    if (this.parent != null) {
      this.parent.propagateExpanded()
    }
  }

  get id() {
    return this.origin.id
  }

  get isRoot() {
    return this.origin.isRoot
  }

  get isGroup() {
    return this.origin.type === ProcType.GROUP
  }

  get visTraceTree() {
    return this.origin.traceTree.visObj
  }

  /**
   * @returns {VisQueryPlan}
   */
  get startVisPlan() {
    return this.visTraceTree.getVisPlan(this.origin.startIdx)
  }

  /**
   * @returns {VisQueryPlan}
   */
  get endVisPlan() {
    return this.visTraceTree.getVisPlan(this.origin.endIdx)
  }

  getTotalStepCnt() {
    return this.origin.endIdx - this.origin.startIdx
  }

  getSimpleName() {
    return this.origin.getSimpleName()
  }

  toString() {
    return this.getSimpleName()
  }

  initLevel(curLevel) {
    this.level = curLevel
    this.children.forEach(child => child.initLevel(curLevel + 1))
  }

  /**
   * Compute the layout of rect, call it recursively
   * @param {ConfigV3} config
   * @param {number} x
   */
  initialLayout(config, x) {
    const {rowHeight} = config.nav
    const {margin} = config.plan

    const barHeightScale = this.origin.traceTree.visObj.stepCntScale

    this.x = x
    this.lineHeight = barHeightScale(this.getTotalStepCnt())
    this.y = (this.level - 1) * rowHeight   // first level (root) will be ignored
    this.width = 0

    if (this.expanded) {
      let startX = x
      for (let i = 0; i < this.children.length; i++) {
        const child = this.children[i]
        child.initialLayout(config, startX)
        startX += child.width
      }
      this.width = startX - x
    } else {
      const startVisPlan = this.startVisPlan
      const endVisPlan = this.endVisPlan
      startVisPlan.layoutOnce(config)
      endVisPlan.layoutOnce(config)
      this.width = (startVisPlan.width + endVisPlan.width) / 2 + margin * 2
    }
  }
}
