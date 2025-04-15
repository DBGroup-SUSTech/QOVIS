import * as d3 from "d3"
import {LinkKind} from "@/js/trace/TransLink"

const EndKind = ['top', 'direct', 'bottom']

export class VisTransLink {
  /** @type {TransLink} */
  origin

  /** @type {VisQueryPlan} */
  srcPlan
  /** @type {VisQueryPlan} */
  dstPlan

  /** @type {VisPlanNode} */
  srcNode
  /** @type {VisPlanNode} */
  dstNode
  /** @type {VisParamItem} */
  srcItem
  /** @type {VisParamItem} */
  dstItem

  /** @type {{x: number, y: number}[]} */
  points = []
  /** @type {{x: number, y: number}} */
  iconPoint = {x: 0, y: 0}
  /** @type {string} */
  path = ''
  /** @type {string} */
  color = '#ff0000'
  highlightColor = '#ff0000'

  // interaction
  fixed = false
  isHighlight = false
  isFixHighlight = false

  constructor(origin) {
    this.origin = origin
  }

  /**
   * @param {VisQueryPlan} srcPlan
   * @param {VisQueryPlan} dstPlan
   * @return {VisTransLink}
   */
  init(srcPlan, dstPlan) {
    this.srcPlan = srcPlan
    this.dstPlan = dstPlan
    this.srcNode = srcPlan.nodeMap.get(this.origin.node0.vid)
    this.dstNode = dstPlan.nodeMap.get(this.origin.node1.vid)
    this.srcItem = this.srcNode.paramMap.get(this.origin.param0)[this.origin.paramIdx0 ?? 0]
    this.dstItem = this.dstNode.paramMap.get(this.origin.param1)[this.origin.paramIdx1 ?? 0]
    return this
  }

  get rules() {
    return this.origin.rules
  }

  get kind() {
    switch (this.origin.kind) {
      case LinkKind.EQ:
        return 'Equal'
      case LinkKind.PEQ:
        return 'Possible equal'
      case LinkKind.CH:
        return 'Changed'
    }
    return 'Unknown'
  }

  /**
   * @param {ConfigV3} config
   */
  /* eslint-disable */
  layout(config) {
    const {nodeSep, rankSep, linkHeight} = config.plan

    const srcPlanX = this.srcPlan.x
    const srcPlanY = this.srcPlan.y
    const dstPlanX = this.dstPlan.x
    const dstPlanY = this.dstPlan.y

    const srcNode = this.srcNode
    const dstNode = this.dstNode

    const startX = srcPlanX + srcNode.x + srcNode.width
    const startY = srcPlanY + srcNode.y + srcNode.height / 2
    const endX = dstPlanX + dstNode.x
    const endY = dstPlanY + dstNode.y + dstNode.height / 2
    const srcPlanRightX = srcPlanX + this.srcPlan.width
    const dstPlanLeftX = dstPlanX - 5

    const [fromKind, fromIdxOffset] = this.getLinkFromKind()
    const [toKind, toIdxOffset] = this.getLinkToKind()
    const prePoints = [], postPoints = []
    let midY0 = 0, midY1 = 0

    switch (fromKind) {
      case 'top':
        const startTopY = srcPlanY + srcNode.levelTopY
        midY0 = startTopY - rankSep / 2 - (fromIdxOffset + 0.5) * linkHeight
        prePoints.push(
            {x: startX, y: startY - srcNode.height / 2},
            {x: startX + nodeSep / 2, y: midY0},
        )
        break
      case 'direct':
        midY0 = startY
        prePoints.push({x: startX, y: startY})
        break
      case 'bottom':
        const startBottomY = srcPlanY + srcNode.levelBottomY
        midY0 = startBottomY + rankSep / 2 + (fromIdxOffset + 0.5) * linkHeight
        prePoints.push(
            {x: startX, y: startY + srcNode.height / 2},
            {x: startX + nodeSep / 2, y: midY0},
        )
        break
    }

    switch (toKind) {
      case 'top':
        const endTopY = dstPlanY + dstNode.levelTopY
        midY1 = endTopY - rankSep / 2 - (toIdxOffset + 0.5) * linkHeight
        postPoints.push(
            {x: endX - nodeSep / 2, y: midY1},
            {x: endX, y: endY - dstNode.height / 2},
        )
        break
      case 'direct':
        midY1 = endY
        postPoints.push({x: endX, y: endY})
        break
      case 'bottom':
        const endBottomY = dstPlanY + dstNode.levelBottomY
        midY1 = endBottomY + rankSep / 2 + (toIdxOffset + 0.5) * linkHeight
        postPoints.push(
            {x: endX - nodeSep / 2, y: midY1},
            {x: endX, y: endY + dstNode.height / 2},
        )
        break
    }

    this.points = [
        ...prePoints,
        {x: srcPlanRightX, y: midY0},
        {x: dstPlanLeftX, y: midY1},
        ...postPoints,
    ]
    this.iconPoint = {x: (srcPlanRightX + dstPlanLeftX) / 2, y: (midY0 + midY1) / 2}

    // this.points = [
    //   {x: startX, y: startY},
    //   {x: srcPlanRightX, y: startY},
    //   {x: srcPlanRightX + (dstPlanX - srcPlanRightX) / 3, y: startY + (endY - startY) / 5},
    //   {x: dstPlanX - (dstPlanX - srcPlanRightX) / 3, y: endY - (endY - startY) / 5},
    //   {x: dstPlanX, y: endY},
    //   {x: endX, y: endY},
    // ]

    // console.log(this.points.map(p => `(${p.x}, ${p.y})`).join(' '))
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveMonotoneX)
    this.path = lineGen(this.points)

    switch(this.origin.kind) {
      case LinkKind.EQ:
      case LinkKind.PEQ:
        this.color = '#4b4b4b'
        this.highlightColor = '#a9a9a9'
        break
      case LinkKind.CH:
        this.color = '#dc7a31'
        this.highlightColor = 'purple'    // useless
        break
    }
  }

  toString() {
    return this.origin.toString()
  }

  getLinkFromKind() {
    const levelOrder = this.srcPlan.outLevelLinkOrders[this.srcNode.level]
    for (let kindIdx = 0; kindIdx < EndKind.length; kindIdx++) {
      const kind = EndKind[kindIdx]
      const orderArray = levelOrder[kindIdx]
      const idx = orderArray.indexOf(this.srcNode)
      if (idx !== -1) {
        switch (kind) {
          case 'top': return [kind, orderArray.length - 1 - idx]
          case 'direct': return [kind, idx]   // idx is 0
          case 'bottom': return [kind, idx]
        }
      }
    }
    throw new Error('cannot find link from')
  }

  getLinkToKind() {
    const levelOrder = this.dstPlan.inLevelLinkOrders[this.dstNode.level]
    for (let kindIdx = 0; kindIdx < EndKind.length; kindIdx++) {
      const kind = EndKind[kindIdx]
      const orderArray = levelOrder[kindIdx]
      const idx = orderArray.indexOf(this.dstNode)
      if (idx !== -1) {
        switch (kind) {
          case 'top': return [kind, orderArray.length - 1 - idx]
          case 'direct': return [kind, idx]   // idx is 0
          case 'bottom': return [kind, idx]
        }
      }
    }
    throw new Error('cannot find link to')
  }

  getTooltipText() {
    const uniqueRules = []
    const ruleName2Count = new Map()
    for (const rule of this.rules) {
      if (!ruleName2Count.has(rule)) {
        uniqueRules.push(rule)
        ruleName2Count.set(rule, 0)
      }
      ruleName2Count.set(rule, ruleName2Count.get(rule) + 1)
    }
    const ruleDataPairs = uniqueRules
        .filter(rule => rule !== '')
        .map(rule => {
          return `${rule} (x${ruleName2Count.get(rule)})`
        })
    return `${this.kind}\n${ruleDataPairs.join('\n')}`
  }

  /**
   * @param {VisParamItem} item
   * @returns {boolean}
   */
  connectTo(item) {
    return this.dstNode === item.node.visObj
        && this.origin.param1 === item.paramKind
        && this.origin.paramIdx1 === item.paramIdx
  }

  /**
   * @param {VisParamItem} item
   * @returns {boolean}
   */
  connectFrom(item) {
    return this.srcNode === item.node.visObj
        && this.origin.param0 === item.paramKind
        && this.origin.paramIdx0 === item.paramIdx
  }

  highlight() {
    this.isHighlight = true
    this.srcItem.highlightForwardIterative()
    this.dstItem.highlightBackwardIterative()
  }

  unhighlight() {
    this.isHighlight = false
    this.srcItem.unhighlightForwardIterative()
    this.dstItem.unhighlightBackwardIterative()
  }

  fixHighlight() {
    this.fixed = true
    this.isFixHighlight = true
    this.srcItem.fixHighlightForwardIterative(0)
    this.dstItem.fixHighlightBackwardIterative(0)
  }

  unfixHighlight() {
    this.fixed = false
    this.isFixHighlight = false
    this.srcItem.unfixHighlightForwardIterative(0)
    this.dstItem.unfixHighlightBackwardIterative(0)
  }
}
