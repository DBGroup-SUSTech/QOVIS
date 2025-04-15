import assert from "assert"
import * as d3 from "d3"
// eslint-disable-next-line no-unused-vars
import {PlanBlock} from "@/js/trace/PlanBlock"
import {TransPath} from "@/js/trace/TransPath"

export class VisTraceTree {
  /** @type {TraceTree} */
  origin

  /** @type {VisTraceNode} */
  root
  /** @type {PlanBlock[]} */
  planBlocks = []

  /** @type {Map<string, number>} */
  colorMap = new Map()
  color = d3.scaleOrdinal(d3.schemeCategory10.concat(d3.schemeAccent))

  /** @type {VisTraceNode[]} */
  selectedNodes = []
  /** @type {(VisQueryPlan | null)[]} */
  visPlans = []    // size = size of selectedNodes + 1. this is a cache for all visPlans
  /** @type {VisQueryPlan[]} */
  visSelectedPlans = []

  /** @type {VisTransPath[]} */
  visTransPaths = []

  /** @type {d3.scaleLinear} */
  stepCntScale = d3.scaleLinear().domain([0, 1]).range([0, 1])

  // layout
  width = 0
  height = 0
  startX = 0
  startY = 0

  maxLevel = 0
  planDagStartY = 0

  /**
   * @param {TraceTree} traceTree
   */
  constructor(traceTree) {
    this.origin = traceTree
  }

  /**
   * @param {ConfigV3} config
   */
  // eslint-disable-next-line no-unused-vars
  init(config) {
    const {maxBarHeight, minBarHeight} = config.nav
    this.stepCntScale
        .domain([1, this.origin.maxFirstLevelStepCnt])
        .range([minBarHeight, maxBarHeight])

    this.selectedNodes = []
    this.visPlans = this.origin.trace.plans.map(() => null)

    // init root
    this.root = this.origin.root.createVisObj()
    this.root.init(null)
    this.root.setExpanded(true)

    this.root.initLevel(0)

    console.log(this.root)
  }

  /**
   * @param {ConfigV3} config
   */
  initialLayout(config) {
    this.updateNavLayout(config)
    this.root.initialLayout(config, 0)
    this.initPlanBlocks(config)
    this.initTransforms(config)
    this.updateLayout(config)
    this.initColorMap()
  }

  updateNavLayout(config) {
    const {rowHeight, planDagMarginTop} = config.nav
    this.selectedNodes = this.getSelectedNodes()
    this.maxLevel = this.selectedNodes.reduce((acc, cur) => Math.max(acc, cur.level), 0)
    this.planDagStartY = this.maxLevel * rowHeight + planDagMarginTop
  }

  /**
   * @param {ConfigV3} config
   */
  initPlanBlocks(config) {
    const {rowHeight, blockRadius} = config.nav

    const visPlans = [this.selectedNodes[0].startVisPlan, ...this.selectedNodes.map(node => node.endVisPlan)]
    this.visSelectedPlans = visPlans
    this.planBlocks = visPlans.map((visPlan, i) => new PlanBlock(this, this.root, i, visPlan))

    /* compute layout of each block rect */

    const firstBlock = this.planBlocks[0]
    const firstNode = this.selectedNodes[0]
    firstBlock.centerX = 0
    firstBlock.topY = 0
    firstBlock.radius = blockRadius
    firstBlock.rectHeight = rowHeight * (firstNode.level - 1)

    for (let i = 1; i < this.planBlocks.length - 1; i++) {
      const leftNode = this.selectedNodes[i - 1]
      const rightNode = this.selectedNodes[i]
      const planBlock = this.planBlocks[i]

      // find the common ancestor of leftNode and rightNode
      const ancestor = this.getCommonAncestor(leftNode, rightNode)

      planBlock.centerX = rightNode.x
      planBlock.topY = ancestor.y + rowHeight   // start at the row below the common ancestor
      planBlock.radius = blockRadius
      planBlock.rectHeight = rowHeight * (Math.max(leftNode.level, rightNode.level) - ancestor.level - 1)
    }

    const lastBlock = this.planBlocks[this.planBlocks.length - 1]
    const lastNode = this.selectedNodes[this.selectedNodes.length - 1]
    lastBlock.centerX = this.root.x + this.root.width
    lastBlock.topY = 0
    lastBlock.radius = blockRadius
    lastBlock.rectHeight = rowHeight * (lastNode.level - 1)

    // initial layout of visPlan
    for (const planBlock of this.planBlocks) {
      const visPlan = planBlock.visPlan
      visPlan.y = this.planDagStartY
      visPlan.x = planBlock.centerX - visPlan.width / 2
    }
  }

  initTransforms(config) {
    const visTransPaths = []
    const linksMap = this.origin.trace.linksMap
    for (const traceNode of this.selectedNodes) {
      const vp0 = traceNode.startVisPlan, vp1 = traceNode.endVisPlan
      const transPath = new TransPath().init(vp0.origin, vp1.origin, false, [], [])
      transPath.links = linksMap.get(traceNode.id)
      if (transPath.links === undefined) {
        console.error('transPath.links is undefined', traceNode, linksMap)
      }
      const visTransPath = transPath.createVisObj().init()
      visTransPaths.push(visTransPath)
    }
    this.visTransPaths = visTransPaths

    // refine visPlans with visTransPaths
    const visPlans = this.visSelectedPlans
    for (let i = 0; i < visPlans.length - 1; i++) {
      const vp0 = visPlans[i], vp1 = visPlans[i + 1]
      const transPath = this.visTransPaths[i]
      vp0.nextTransPath = transPath
      vp1.prevTransPath = transPath
    }
    for (const vp of visPlans) {
      vp.nodes.forEach(v => v.initItemLinks(vp))
      vp.refineLayoutWithTransPath(config)
    }
  }


  /**
   * @param {VisTraceNode} leftNode
   * @param {VisTraceNode} rightNode
   * @returns {VisTraceNode}
   */
  getCommonAncestor(leftNode, rightNode) {
    const leftPath = []
    let node = leftNode
    while (node !== null) {
      leftPath.push(node)
      node = node.parent
    }
    const rightPath = []
    node = rightNode
    while (node !== null) {
      rightPath.push(node)
      node = node.parent
    }
    // find the joint node of leftPath and rightPath
    let i = 0, j = 0
    let paths = [leftPath, rightPath]
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const x = paths[0][i]
      const y = paths[1][j]
      if (x === y) {
        return x
      }
      if (i >= paths[0].length - 1) {
        // paths[0] is leftPath
        paths[0] = rightPath
        i = 0
      } else {
        i += 1
      }
      if (j >= paths[1].length - 1) {
        // paths[1] is rightPath
        paths[1] = leftPath
        j = 0
      } else {
        j += 1
      }
    }
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

  /**
   * @param {ConfigV3} config
   */
  // eslint-disable-next-line no-unused-vars
  updateLayout(config) {
    const {margin} = config.plan

    this.width = this.root.width
        + this.planBlocks[0].visPlan.width / 2
        + this.planBlocks[this.planBlocks.length - 1].visPlan.width / 2
        + margin * 2
    this.height = this.planBlocks.reduce((acc, cur) => Math.max(acc, cur.visPlan.y + cur.visPlan.height), 0)
        + margin
    this.startX = margin + this.planBlocks[0].visPlan.width / 2
    this.startY = 0

    this.visTransPaths.forEach(transPath => {
      if (transPath === null) {
        return
      }
      transPath.layout(config)
    })
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
    return nodes
  }

  getVisPlan(idx) {
    assert(idx >= 0 && idx < this.visPlans.length, 'Invalid idx ' + idx)
    let visPlan = this.visPlans[idx]
    if (visPlan === null) {
      const plan = this.origin.trace.plans[idx]
      visPlan = plan.createVisObj()
      this.visPlans[idx] = visPlan
    }
    return visPlan
  }

  /**
   * @param {ConfigV3} config
   * @param {VisTraceNode} node
   */
  toggleTraceNode(config, node) {
    node.setExpanded(!node.expanded)
    // temp
    this.updateNavLayout(config)
    this.root.initialLayout(config, 0)
    this.initPlanBlocks(config)
    this.initTransforms(config)
    this.updateLayout(config)
  }
}

