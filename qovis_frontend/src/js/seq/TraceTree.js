import assert from "assert"
import {getTextBoundingSize} from "@/utils/Layout"
import * as d3 from "d3"

/**
 * @enum {string}
 * @readonly
 */
export const NodeType = {
  ROOT: 'root',
  PHASE: 'phase',
  BATCH: 'batch',
  ACTION: 'action',
}

export class TraceTree {
  /** @type {TraceNode} */
  root = new TraceNode(NodeType.ROOT)
  /** @type {Map<string, number>} */
  colorMap = new Map()
  color = d3.scaleOrdinal(d3.schemeCategory10.concat(d3.schemeAccent))
  sizeScale = d3.scaleLinear()

  // layout
  width = 0
  height = 0

  /**
   * @param {ConfigV2} config
   * @param {DynamicGraph} dg
   */
  constructor(config, dg) {
    const plans = dg.plans
    const phaseIntervals = dg.phaseIntervals
    const phaseNames = dg.phaseNames

    // init root
    this.root.init(null, 'root', plans)
    this.root.setExpanded(true)

    const phaseNodes = []
    for (let i = 0; i < phaseIntervals.length; i++) {
      const [start, end] = phaseIntervals[i]
      const planSlice = plans.slice(start + 1, end)
      const phaseName = phaseNames[i]

      const phaseNode = new TraceNode(NodeType.PHASE)
      phaseNode.init(this.root, phaseName, planSlice)

      phaseNodes.push(phaseNode)
    }
    this.root.children = phaseNodes

    for (const phaseNode of this.root.children) {
      const phasePlans = phaseNode.plans

      // split phase plans to batch

      const batchPlansList = []
      let batchPlans = [phasePlans[0]]
      const getBatchId = (index) => {
        const plan = phasePlans[index]
        if (plan.meta.batchId == null && index < phasePlans.length - 1) {
          return getBatchId(index + 1)
        } else {
          return plan.meta.batchId ?? ''
        }
      }
      for (let i = 1; i < phasePlans.length; i++) {
        const p1 = phasePlans[i]
        if (getBatchId(i - 1) === getBatchId(i)) {
          batchPlans.push(p1)
        } else {
          batchPlansList.push(batchPlans)
          batchPlans = [p1]
        }
      }
      if (batchPlans.length !== 0) {
        batchPlansList.push(batchPlans)
      }

      // create batch nodes
      for (const batchPlans of batchPlansList) {
        const batchNode = new TraceNode(NodeType.BATCH)
        batchNode.init(phaseNode, batchPlans[0].meta.batchName, batchPlans)
        phaseNode.children.push(batchNode)

        // create action nodes

        for (const plan of batchPlans) {
          const actionNode = new TraceNode(NodeType.ACTION)
          actionNode.init(batchNode, plan.meta.name, [plan])
          batchNode.children.push(actionNode)
        }
      }
    }

    console.log(this.root)
  }

  /**
   * @param {ConfigV2} config
   */
  initialLayout(config) {
    this.root.initialLayout(config)
    this.root.x = 5
    this.root.y = 5
    this.updateLayout(config)
    this.initColorMap()
    this.initSizeScale(config)
  }

  initColorMap() {
    let idx = 0
    const collectColor = (node) => {
      const name = node.getSimpleName()
      if (!this.colorMap.has(name)) {
        this.colorMap.set(name, idx++)
      }
      for (const child of node.children) {
        collectColor(child)
      }
    }

    collectColor(this.root)
  }

  getColor(node) {
    const name = node.getSimpleName()
    const idx = this.colorMap.get(name)
    return this.color(idx % 10)
  }

  initSizeScale(config) {
    const {minRadius, maxRadius} = config.traceNode
    // const maxRatio = Math.max(...this.root.children.map(child => child.planRatio))
    // this.sizeScale.domain([0, maxRatio]).range([minRadius, maxRadius])
    this.sizeScale.domain([1/this.root.plans.length, 1]).range([minRadius, maxRadius])
  }

  updateLayout() {
    this.width = this.root.width + 10
    this.height = this.root.height + 10
  }
}

export class TraceNode {
  /** @type {TraceNode} */
  parent = null
  /** @type {TraceNode[]} */
  children = []
  /** @type {NodeType} */
  nodeType
  /** @type {string} */
  name = 'Unknown'
  /** @type {Plan[]} */
  plans = []

  // layout
  x = 0
  y = 0
  expandedLayout = {
    width: 0,
    height: 0,
  }
  collapsedLayout = {
    width: 0,
    height: 0,
  }
  layoutPtr

  color = '#000000'

  _rotateTextSize

  // interaction
  expanded

  constructor(nodeType) {
    this.nodeType = nodeType
    this.setExpanded(false)
  }

  get width() {
    return this.layoutPtr.width
  }

  get height() {
    return this.layoutPtr.height
  }

  get planRatio() {
    if (this.isRoot) return 0
    return this.plans.length / this.parent.plans.length
  }

  getSimpleName() {
    let name = this.name
    if (!name || name === '') {
      name = 'Unknown'
    }
    if (name.endsWith("$")) {
      name = name.substring(0, name.length - 1)
    }
    if (name.includes('.')) {
      name = name.split('.')[1]
    }
    if (name.includes("$")) {
      name = name.split("$")[1]
    }
    return name
  }

  setExpanded(expanded) {
    this.expanded = expanded
    this.layoutPtr = expanded ? this.expandedLayout : this.collapsedLayout
  }

  /**
   * @param {TraceNode} parent
   * @param {string} name
   * @param {Plan[]} plans
   */
  init(parent, name, plans) {
    this.parent = parent
    this.name = name
    this.plans = plans
  }

  get isRoot() {
    return this.nodeType === NodeType.ROOT
  }

  /**
   * @returns {{width: number, height: number}}
   */
  get rotateTextSize() {
    if (this._rotateTextSize == null) {
      const {width, height} = getTextBoundingSize(this.name, {rotate: 20})
      this._rotateTextSize = {width, height}
    }
    return this._rotateTextSize
  }

  toString() {
    return this.name
  }

  /**
   * @param {ConfigV2} config
   */
  initialLayout(config) {
    const {initialWidth, initialHeight, marginY, textOffsetX, textOffsetY, textRotation} = config.traceNode

    this.layoutPtr = this.expanded ? this.expandedLayout : this.collapsedLayout
    this.children.forEach(child => child.initialLayout(config))
    this.computeExpandedLayout(config)

    // compute collapsedLayout
    const {width: textWidth, height: textHeight} = getTextBoundingSize(this.name, {rotate: textRotation})

    Object.assign(this.collapsedLayout, {
      width: Math.max(initialWidth, initialWidth / 2 - textOffsetX + textWidth),
      height: initialHeight + marginY + textHeight - textOffsetY,
    })
  }

  /**
   * Compute expandedLayout without recursion
   *
   * @param {ConfigV2} config
   */
  computeExpandedLayout(config) {
    const {paddingX, marginX, marginY, initialWidth, initialHeight, textOffsetX} = config.traceNode

    // compute expandedLayout
    if (this.children.length !== 0) {
      const childHeight = this.isRoot ? 0 : initialHeight

      // compute x & y for each child
      let x = paddingX
      let maxTextX = 0
      for (let i = 0; i < this.children.length; i++) {
        const child = this.children[i]

        x += marginX
        if (i !== 0 && !this.children[i - 1].expanded && child.expanded) {
          // text of previous unexpanded node(s) will overlap with the current node (expanded)
          x = Math.max(x, maxTextX + marginX)
        }
        child.x = x
        child.y = childHeight
        x += (child.expanded ? child.width : initialWidth) + marginX

        if (!child.expanded) {
          maxTextX = Math.max(maxTextX, x + textOffsetX - initialWidth / 2 + child.rotateTextSize.width)
        }
      }

      // compute width & height
      let maxChildHeight = 0
      for (const child of this.children) {
        maxChildHeight = Math.max(maxChildHeight, child.height)
      }
      const {width: textWidth} = getTextBoundingSize(this.name)
      const lastChild = this.children[this.children.length - 1]

      Object.assign(this.expandedLayout, {
        width: Math.max(x,
                lastChild.expanded ? x : (x - initialWidth / 2 + textOffsetX + lastChild.rotateTextSize.width),
                initialWidth + textWidth)
            + paddingX,
        height: initialHeight + marginY + maxChildHeight,
      })

    } else {
      const {width: textWidth} = getTextBoundingSize(this.name)

      Object.assign(this.expandedLayout, {
        width: initialWidth + textWidth + paddingX,
        height: initialHeight,
      })
    }
  }

  // /**
  //  * @param {ConfigV2} config
  //  */
  // layout(config) {
  //   const {paddingX, marginX, marginY, initialWidth, initialHeight} = config.traceNode
  //
  //   if (this.children.length === 0) {
  //     this.width = initialWidth
  //     this.height = initialHeight
  //     return
  //   }
  //
  //   this.children.forEach(child => child.layout(config))
  //
  //   const childHeight = this.isRoot ? 0 : initialHeight
  //
  //   let x = paddingX + marginX
  //   for (const child of this.children) {
  //     child.x = x
  //     child.y = childHeight
  //     x += child.width + marginX
  //   }
  //   x += paddingX
  //
  //   this.width = x
  //   this.height = initialHeight + marginY + this.children.reduce((acc, child) => Math.max(acc, child.height), 0)
  // }

  /**
   * Updates layout after expanding/collapsing
   * @param {ConfigV2} config
   */
  updateLayout(config) {
    const {initialWidth, textOffsetX} = config.traceNode

    let deltaWidth, deltaHeight

    if (this.expanded) {
      // not expanded -> expanded

      // update expandedLayout first
      this.computeExpandedLayout(config)

      deltaWidth = this.expandedLayout.width - this.collapsedLayout.width
      deltaHeight = this.expandedLayout.height - this.collapsedLayout.height
    } else {
      // expanded -> not expanded
      deltaWidth = this.collapsedLayout.width - this.expandedLayout.width
      deltaHeight = this.collapsedLayout.height - this.expandedLayout.height
    }

    // update all nodes after it / update parent nodes

    let parent = this.parent, child = this
    while (parent) {
      assert(parent.expanded)
      const index = parent.children.indexOf(child)
      let deltaX = 0
      if (child === this && index !== 0) {
        const prevChild = parent.children[index - 1]
        if (this.expanded && !prevChild.expanded) {
          deltaX = prevChild.rotateTextSize.width - textOffsetX - initialWidth / 2
        } else if (!this.expanded && !prevChild.expanded) {
          deltaX -= prevChild.rotateTextSize.width - textOffsetX - initialWidth / 2
        }
        this.x += deltaX
      }
      for (let i = index + 1; i < parent.children.length; i++) {
        parent.children[i].x += deltaX + deltaWidth
      }
      parent.expandedLayout.width += deltaWidth
      parent.expandedLayout.height += deltaHeight

      child = parent
      parent = parent.parent
    }
  }
}
