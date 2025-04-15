import assert from "assert"
import {getTextBoundingSize} from "@/utils/Layout"
import * as d3 from "d3"
import {VPlanDag} from "@/js/native/VPlanDag"
import {kmeans} from "ml-kmeans"

/**
 * @enum {string}
 * @readonly
 */
export const NodeType = {
  ROOT: 'root',
  PHASE_PATTERN: 'phase_pattern',
  PHASE: 'phase',
  BATCH_PATTERN: 'batch_pattern',
  BATCH: 'batch',
  ACTION_PATTERN: 'action_pattern',
  ACTION: 'action',
}

export class PatternTraceTree {
  /** @type {PatternTraceNode} */
  root = new PatternTraceNode(NodeType.ROOT)
  /** @type {Map<string, number>} */
  colorMap = new Map()
  color = d3.scaleOrdinal(d3.schemeCategory10.concat(d3.schemeAccent))
  sizeScale = d3.scaleLinear()

  /** @type {Map<string, Pattern>} */
  patternMap = new Map()

  // layout
  width = 0
  height = 0

  /** @type {PatternTraceNode[]} */
  selectedNodes = []
  /** @type {VPlanDag[]} */
  vPlanDags = []
  freqCost = 0
  timeCost = 0

  /**
   * @param {ConfigV2} config
   * @param {DynamicGraph} dg
   * @param {Pattern[]} patterns
   */
  constructor(config, dg, patterns) {
    const plans = dg.plans
    const phaseIntervals = dg.phaseIntervals
    const phaseNames = dg.phaseNames.map(name => {
      if (name.includes('#')) {
        return name.split('#')[0]
      } else {
        return name
      }
    })

    const patternMap = this.patternMap = new Map()
    for (const pattern of patterns) {
      patternMap.set(pattern.name, pattern)
    }

    // init root
    this.root.init(null, 'root', plans)
    this.root.setExpanded(true)

    const rootPattern = this.patternMap.get("Root")
    const matchGroups = this.matchPattern(rootPattern, phaseNames)
    console.log(rootPattern, matchGroups)

    const tmpPhaseIntervals = [...phaseIntervals]
    const tmpPhaseNames = [...phaseNames]
    for (let i = 0; i < rootPattern.items.length; i++) {
      const phasePatternNode = new PatternTraceNode(NodeType.PHASE_PATTERN)
      const group = matchGroups[i]
      const intervals = tmpPhaseIntervals.splice(0, group.length)

      const tmpPlans = []
      for (const interval of intervals) {
        const [start, end] = interval
        tmpPlans.push(...plans.slice(start + 1, end))
      }
      const patternItem = rootPattern.items[i]
      phasePatternNode.init(this.root, patternItem.name, tmpPlans, patternItem.desc)
      this.root.children.push(phasePatternNode)

      for (let j = 0; j < group.length; j++) {
        const [start, end] = intervals[j]
        const planSlice = plans.slice(start + 1, end)
        const phaseName = tmpPhaseNames.shift()

        const phaseNode = new PatternTraceNode(NodeType.PHASE)
        phaseNode.init(phasePatternNode, phaseName, planSlice)
        phasePatternNode.children.push(phaseNode)
      }
    }

    for (const phasePatternNode of this.root.children) {
      for (const phaseNode of phasePatternNode.children) {
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

        const batchNames = batchPlansList.map(batchPlans => this.inferBatchName(batchPlans))

        const phasePattern = this.patternMap.get(phaseNode.name)
        const matchGroups = this.matchPattern(phasePattern, batchNames)

        const tmpBatchPlansList = [...batchPlansList]
        const tmpBatchNames = [...batchNames]
        for (let i = 0; i < phasePattern.items.length; i++) {
          const batchPatternNode = new PatternTraceNode(NodeType.BATCH_PATTERN)
          const group = matchGroups[i]
          const groupBatchPlans = tmpBatchPlansList.splice(0, group.length)
          const tmpPlans = groupBatchPlans.flat()
          batchPatternNode.init(phaseNode, phasePattern.items[i].name, tmpPlans, phasePattern.items[i].desc)
          phaseNode.children.push(batchPatternNode)

          for (let j = 0; j < group.length; j++) {
            const planSlice = groupBatchPlans[j]
            const batchName = tmpBatchNames.shift()

            const batchNode = new PatternTraceNode(NodeType.BATCH)
            batchNode.init(batchPatternNode, batchName, planSlice)
            batchPatternNode.children.push(batchNode)
          }
        }

        for (const batchPatternNode of phaseNode.children) {
          for (const batchNode of batchPatternNode.children) {
            const batchPlans = batchNode.plans
            const actionNames = batchPlans.map(p => p.meta.getSimpleName())

            const batchPattern = this.patternMap.get(batchNode.name)
            const matchGroups = this.matchPattern(batchPattern, actionNames)

            const tmpPlans = [...batchPlans]
            const tmpNames = [...actionNames]
            for (let i = 0; i < batchPattern.items.length; i++) {
              const actionPatternNode = new PatternTraceNode(NodeType.ACTION_PATTERN)
              const group = matchGroups[i]
              const groupPlans = tmpPlans.splice(0, group.length)
              const pattern = batchPattern.items[i]
              actionPatternNode.init(batchNode, pattern.name, groupPlans, pattern.desc)
              batchNode.children.push(actionPatternNode)

              for (let j = 0; j < group.length; j++) {
                const plan = groupPlans[j]
                const actionName = tmpNames.shift()

                const actionNode = new PatternTraceNode(NodeType.ACTION)
                actionNode.init(actionPatternNode, actionName, [plan])
                actionPatternNode.children.push(actionNode)
              }
            }
          }
        }

      }
    }

    console.log(this.root)
  }

  inferBatchName(batchPlans) {
    const firstName = batchPlans[0].meta.batchName
    if (firstName === "Planning") return "Prepare Planning"
    if (firstName != null) return firstName
    if (batchPlans[0].meta.getSimpleName() === 'SpecialLimits') {
      return "Physical Planning"
    }
  }

  /**
   * @param {Pattern} pattern
   * @param {string[]} names
   * @returns {string[][]}
   */
  matchPattern(pattern, names) {
    let p = 0, q = 0
    const items = pattern.items
    const matchGroups = items.map(() => [])
    const isMatched = (s, p) => s === p || s === 'SoftTrans'
    while (p < items.length && q < names.length) {
      const item = items[p]
      let name = names[q]
      switch (item.desc) {
        case "":
          assert(isMatched(name, item.name))
          matchGroups[p].push(name)
          p++
          q++
          break
        case "+":
          while (isMatched(name, item.name)) {
            matchGroups[p].push(name)
            q++
            if (q >= names.length) break
            name = names[q]
          }
          p++
          break
        case "?":
          if (isMatched(name, item.name)) {
            matchGroups[p].push(name)
            p++
            q++
          } else {
            p++
          }
          break
        case "*":
          while (isMatched(name, item.name)) {
            matchGroups[p].push(name)
            q++
            if (q >= names.length) break
            name = names[q]
          }
          p++
          break
        default:
          assert(false)
      }
    }
    if (matchGroups.reduce((acc, cur) => acc + cur.length, 0) !== names.length){
      console.log(pattern, matchGroups, names)
    }
    assert(matchGroups.reduce((acc, cur) => acc + cur.length, 0) === names.length)
    return matchGroups
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

  getSelectedNodes() {
    const nodes = []
    const collect = (node) => {
      if (!node.expanded) {
        nodes.push(node)
      } else {
        for (const child of node.children) {
          collect(child)
        }
      }
    }
    collect(this.root)
    return nodes.filter(node => node.plans.length > 0)
  }

  /**
   * @param {ConfigV1} config
   */
  computeVPlanDags(config) {
    this.selectedNodes = this.getSelectedNodes()
    const startDag = (new VPlanDag()).init(this.root.plans[0])
    this.vPlanDags = [startDag, ...this.selectedNodes.map(node => node.vPlanDag)]
    this.vPlanDags.forEach(vPlanDag => vPlanDag.layoutOnce(config))
    console.log(this.selectedNodes, this.vPlanDags)

    // update freqCost
    const logicalNodeCnt = this.selectedNodes
        .map(node => {
          if (node.isPatternNode()) {
            return node.children.length
          } else {
            return 1
          }
        })
        .reduce((acc, cur) => acc + cur, 0)
    let visNodeCnt = -1
    const collect = (node) => {
      visNodeCnt += 1
      if (node.expanded) {
        for (const child of node.children) {
          collect(child)
        }
      }
    }
    collect(this.root)
    this.freqCost = visNodeCnt / logicalNodeCnt

    // update timeCost
    const data = this.selectedNodes.map(node => [node.getTimeCost()])
    let ans = kmeans(data, 2, {});
    console.log(ans)
    const info = ans.computeInformation(data)
    let smallCnt, largeCnt
    if (ans.centroids[0] < ans.centroids[1]) {
      smallCnt = info[0].size
      largeCnt = info[1].size
    } else {
      smallCnt = info[1].size
      largeCnt = info[0].size
    }
    console.log('Time cost: ', smallCnt, largeCnt, smallCnt / largeCnt)
    this.timeCost = smallCnt / largeCnt
  }
}

export class PatternTraceNode {
  /** @type {PatternTraceNode} */
  parent = null
  /** @type {PatternTraceNode[]} */
  children = []
  /** @type {NodeType} */
  nodeType
  /** @type {string} */
  name = 'Unknown'
  /** @type {Plan[]} */
  plans = []
  desc

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

  _vPlanDag = null

  constructor(nodeType) {
    this.nodeType = nodeType
    this.setExpanded(false)
  }

  isPatternNode() {
    return this.nodeType.includes('pattern')
  }

  get vPlanDag() {
    if (!this._vPlanDag && this.plans.length > 0) {
      this._vPlanDag = new VPlanDag()
      this._vPlanDag.init(this.plans[this.plans.length - 1])
    }
    return this._vPlanDag
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

  getTimeCost() {
    return this.plans.reduce((acc, cur) => acc + cur.meta.runTime ?? 0, 0)
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

  getSimpleNameWithCnt() {
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
    if (this.isPatternNode() && this.children.length > 1) {
      name += ` (${this.children.length})`
    }
    return name
  }

  setExpanded(expanded) {
    this.expanded = expanded
    this.layoutPtr = expanded ? this.expandedLayout : this.collapsedLayout
  }

  /**
   * @param {PatternTraceNode} parent
   * @param {string} name
   * @param {Plan[]} plans
   * @param {?string} desc
   */
  init(parent, name, plans, desc=null) {
    this.parent = parent
    this.name = name
    this.plans = plans
    this.desc = desc
  }

  get isRoot() {
    return this.nodeType === NodeType.ROOT
  }

  /**
   * @returns {{width: number, height: number}}
   */
  get rotateTextSize() {
    if (this._rotateTextSize == null) {
      const text = this.getSimpleNameWithCnt()
      const {width, height} = getTextBoundingSize(text, {rotate: 20})
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
    const text = this.getSimpleNameWithCnt()
    const {width: textWidth, height: textHeight} = getTextBoundingSize(text, {rotate: textRotation})

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
      const text = this.getSimpleNameWithCnt()
      const {width: textWidth} = getTextBoundingSize(text)
      const lastChild = this.children[this.children.length - 1]

      Object.assign(this.expandedLayout, {
        width: Math.max(x,
                lastChild.expanded ? x : (x - initialWidth / 2 + textOffsetX + lastChild.rotateTextSize.width),
                initialWidth + textWidth)
            + paddingX,
        height: initialHeight + marginY + maxChildHeight,
      })

    } else {
      const text = this.getSimpleNameWithCnt()
      const {width: textWidth} = getTextBoundingSize(text)

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
