import {Graph} from "@/js/common/Graph"
import dagre from "dagre"
import * as d3 from "d3"
import {getTextSize} from "@/utils/Layout"
import {VisPlanEdge} from "@/js/trace/VisPlanEdge"
import {VisPlanNode} from "@/js/trace/VisPlanNode"

/**
 * @extends {Graph<VisPlanNode, VisPlanEdge>}
 */
export class VisQueryPlan extends Graph {
  /** @type {import('@/js/trace/QueryPlan').QueryPlan} */
  origin = null

  /** @type {VisPlanNode} */
  root
  /** @type {VisPlanNode[][]} */
  levels = []

  // compute and update by outer object
  x
  y
  // compute by itself
  height
  width

  /** @type {number[]} */
  levelGaps = []
  /** @type {number[]} */
  rowHeights = []
  /** @type {VisTransPath | null} */
  prevTransPath = null
  /** @type {VisTransPath | null} */
  nextTransPath = null
  /** @type {VisPlanNode[][][]} */
  inLevelLinkOrders = []    // level -> (top, direct, bottom) -> node[]
  /** @type {VisPlanNode[][][]} */
  outLevelLinkOrders = []

  _beLayout = false

  constructor() {
    super()
  }

  /**
   * @param {import('@/js/trace/QueryPlan').QueryPlan} plan
   * @returns {this}
   */
  init(plan) {
    this.origin = plan

    this.nodes = []
    this.nodeMap = new Map()
    for (const v of plan.nodes) {
      const node = new VisPlanNode()
      node.init(v.vid)
      node.assignOrigin(v)
      v.visObj = node
      this.nodes.push(node)
      this.nodeMap.set(node.vid, node)
    }

    for (const parent of plan.nodes) {
      const dst = this.nodeMap.get(parent.vid)
      for (const child of parent.children) {
        const src = this.nodeMap.get(child.vid)
        const edge = new VisPlanEdge()
        edge.init(src, dst)

        this.edges.push(edge)
        this.edgeMap.set(edge.eid, edge)
        src.outEdges.push(edge)
        dst.inEdges.push(edge)
      }
    }

    this.root = this.nodeMap.get(plan.root.vid)

    /** @type {VisPlanNode[][]} */
    this.levels = []
    const root = this.root
    const queue = [root]
    while (queue.length > 0) {
      const curLevel = []
      const len = queue.length
      for (let i = 0; i < len; i++) {
        const node = queue.shift()
        curLevel.push(node)
        queue.push(...node.children)
      }
      this.levels.push(curLevel)
    }

    for (let i = 0; i < this.levels.length; i++) {
      for (const node of this.levels[i]) {
        node.level = i
      }
    }

    return this
  }

  /**
   * @param {ConfigV3} conf
   */
  layoutOnce(conf) {
    if (!this._beLayout) {
      this.layout(conf)
    }
  }

  /**
   * @param {ConfigV3} conf
   */
  layout(conf) {
    const {padding} = conf.plan

    if (this.nodes.length === 0) {
      this.width = 30
      this.height = 15
      return
    }

    this.nodes.forEach(node => node.layout(conf))

    // this.layoutTreeDagre(conf)
    this.layoutTreeLevel(conf)

    // compute total size
    this.width = Math.max(...this.nodes.map(node => {
      return node.x + node.width
    })) + padding * 2
    this.height = Math.max(...this.nodes.map(node => {
      return node.y + node.height
    })) + padding * 2
  }

  /**
   * @param {ConfigV3} conf
   */
  layoutTreeDagre(conf) {
    const {nodeWidth, nodeTitleHeight, nodeWidthAlias, paramLimit} = conf.plan
    const {useOptAlias} = conf

    let g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir:'BT',
      ranksep: '10',
      nodesep: '15',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.nodes.forEach(node => {
      node.width = useOptAlias ? nodeWidthAlias : nodeWidth
      const paramCnt = Math.min(node.origin.paramArray.length, paramLimit + 1)
      node.height = nodeTitleHeight + paramCnt * conf.plan.paramRowHeight
      g.setNode(node.vid, node)
    })

    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        const label = edge.planEdgeStr
        if (label === '') {
          g.setEdge({v: edge.src.vid, w: edge.dst.vid})
        } else {
          const {width, height} = getTextSize(label, conf.plan.edgeFontSize)
          g.setEdge({v: edge.src.vid, w: edge.dst.vid}, {label, width, height})
        }
      })
    })

    // this will change the node.x, node.y
    dagre.layout(g)

    // x, y is the center
    this.nodes.forEach(node => {
      node.x -= node.width / 2
      node.y -= node.height / 2
    })

    // compute levelTopY and levelBottomY and levelGaps
    // todo
    this.nodes.forEach(node => {
      node.levelTopY = node.y
      node.levelBottomY = node.y + node.height
    })

    this.g = g
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        const e = g.edge({v: edge.src.vid, w: edge.dst.vid})
        edge.points = e.points
        edge.path = lineGen(edge.points)
        edge.textX = e.x
        edge.textY = e.y
      })
    })
  }

  /**
   * @param {ConfigV3} conf
   */
  layoutTreeLevel(conf) {
    const {rankSep, nodeSep} = conf.plan

    const levels = this.levels

    this.levelGaps = Array.from({length: levels.length + 1}, () => rankSep)
    this.levelGaps[0] = 0

    // // compute height and width for each node first
    // this.nodes.forEach(node => {
    //   node.width = conf.plan.useOptAlias ? conf.plan.nodeWidthAlias : conf.plan.nodeWidth
    //   const paramCnt = Math.min(node.origin.paramArray.length, conf.plan.paramLimit + 1)
    //   node.height = conf.plan.nodeTitleHeight + paramCnt * conf.plan.paramRowHeight
    // })

    this.rowHeights = Array.from({length: levels.length}, () => 0)
    for (let i = 0; i < levels.length; i++) {
      const level = levels[i]
      this.rowHeights[i] = Math.max(...level.map(node => node.height))
    }

    // compute y
    let y = this.levelGaps[0]
    for (let i = 0; i < levels.length; i++) {
      const level = levels[i]
      const rowHeight = this.rowHeights[i]
      for (const node of level) {
        node.y = y + rowHeight / 2 - node.height / 2
        node.levelTopY = y
        node.levelBottomY = y + rowHeight
      }
      y += rowHeight + this.levelGaps[i + 1]
    }

    // compute x
    const computeX = (node, startX) => {
      if (node.children.length === 0) {
        node.x = startX
        return node.width
      } else {
        let width = 0
        for (const child of node.children) {
          width += computeX(child, startX + width)
          width += nodeSep
        }
        width -= nodeSep
        node.x = startX + width / 2 - node.width / 2
        return width
      }
    }
    computeX(this.root, 0)

    // edges
    const lineGen = d3.line().x(p => p[0]).y(p => p[1]).curve(d3.curveBasis)
    this.edges.forEach(edge => {
      const parent = edge.dst
      const child = edge.src

      const pcx = parent.x + parent.width / 2
      const pcy = parent.y + parent.height / 2
      const ccx = child.x + child.width / 2

      // point from the child top center to the parent center

      edge.points = [
        [ccx, child.y],
        [ccx, child.levelTopY - rankSep / 2],
        [pcx, pcy],
      ]
      edge.path = lineGen(edge.points)
      edge.textX = 0
      edge.textY = 0
    })
  }

  /**
   * @param {ConfigV3} conf
   */
  refineLayoutWithTransPath(conf) {
    const {linkHeight, rankSep, padding} = conf.plan

    this.inLevelLinkOrders = Array.from({length: this.levels.length}, () => [[], [], []])
    this.outLevelLinkOrders = Array.from({length: this.levels.length}, () => [[], [], []])

    if (this.prevTransPath !== null) {
      for (let i = 0; i < this.levels.length; i++) {
        const level = this.levels[i]
        const levelLinkOrder = this.inLevelLinkOrders[i]
        for (let j = 0; j < level.length; j++) {
          const node = level[j]
          if (this.prevTransPath.dstVid2Links.get(node.origin.vid).length !== 0) {
            if (j === 0) {
              levelLinkOrder[1].push(node)
            } else {
              levelLinkOrder[0].unshift(node)
            }
          }
        }
      }
    }

    if (this.nextTransPath !== null) {
      for (let i = 0; i < this.levels.length; i++) {
        const level = this.levels[i]
        const levelLinkOrder = this.outLevelLinkOrders[i]
        for (let j = 0; j < level.length; j++) {
          const node = level[j]
          if (this.nextTransPath.srcVid2Links.get(node.origin.vid).length !== 0) {
            if (j === level.length - 1) {
              levelLinkOrder[1].push(node)
            } else {
              levelLinkOrder[2].unshift(node)
            }
          }
        }
      }
    }

    // compute levelGaps
    for (let i = 0; i < this.levelGaps.length; i++) {
      let linkCnt = 0
      if (i !== 0) {
        const aboveInBottom = this.inLevelLinkOrders[i - 1][2]
        const aboveOutBottom = this.outLevelLinkOrders[i - 1][2]
        linkCnt += aboveInBottom.length + aboveOutBottom.length
      }
      if (i !== this.levelGaps.length - 1) {
        const belowInTop = this.inLevelLinkOrders[i][0]
        const belowOutTop = this.outLevelLinkOrders[i][0]
        linkCnt += belowInTop.length + belowOutTop.length
      }
      // console.log(i, linkCnt)
      this.levelGaps[i] = linkCnt * linkHeight + rankSep
    }

    // recompute y
    let y = this.levelGaps[0]
    for (let i = 0; i < this.levels.length; i++) {
      const level = this.levels[i]
      const rowHeight = this.rowHeights[i]
      for (const node of level) {
        node.y = y + rowHeight / 2 - node.height / 2
        node.levelTopY = y
        node.levelBottomY = y + rowHeight
      }
      y += rowHeight + this.levelGaps[i + 1]
    }

    // recompute edges
    const lineGen = d3.line().x(p => p[0]).y(p => p[1]).curve(d3.curveBasis)
    this.edges.forEach(edge => {
      const parent = edge.dst
      const child = edge.src

      const pcx = parent.x + parent.width / 2
      const pcy = parent.y + parent.height / 2
      const ccx = child.x + child.width / 2

      // point from the child top center to the parent center

      edge.points = [
        [ccx, child.y],
        [ccx, child.levelTopY - rankSep / 2],
        [pcx, pcy],
      ]
      edge.path = lineGen(edge.points)
      edge.textX = 0
      edge.textY = 0
    })

    // recompute height
    this.height = Math.max(...this.nodes.map(node => {
      return node.y + node.height
    })) + padding * 2
  }
}

