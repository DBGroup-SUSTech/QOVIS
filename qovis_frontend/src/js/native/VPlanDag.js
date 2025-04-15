import {Graph, Node, Edge} from "@/js/common/Graph"
import dagre from "dagre"
import * as d3 from "d3"

/**
 * @extends {Graph<VPlanNode, VPlanEdge>}
 */
export class VPlanDag extends Graph {
  /** @type {Plan} */
  plan

  // compute and update by outer object
  x
  y
  // compute by itself
  height
  width

  _beLayout = false

  constructor() {
    super()
  }

  /**
   * @param {Plan} plan
   * @returns {VPlanDag}
   */
  init(plan) {
    this.plan = plan

    this.nodes = []
    this.nodeMap = new Map()
    for (const v of plan.nodeMap.values()) {
      const node = new VPlanNode()
      node.init(v.vid)
      node.planNode = v
      this.nodes.push(node)
      this.nodeMap.set(node.vid, node)
    }

    for (const e of plan.edgeMap.values()) {
      const src = this.nodeMap.get(e.provider.vid)
      const dst = this.nodeMap.get(e.consumer.vid)
      const edge = new VPlanEdge()
      edge.init(src, dst)
      edge.planEdge = e
      this.edges.push(edge)
      this.edgeMap.set(edge.eid, edge)
    }

    for (const v of plan.nodeMap.values()) {
      const node = this.nodeMap.get(v.vid)
      for (const p of v.providers) {
        const child = this.nodeMap.get(p.vid)
        const edge = this.edgeMap.get(VPlanEdge.getEid(child, node))
        node.inEdges.push(edge)
      }
      for (const c of v.consumers) {
        const parent = this.nodeMap.get(c.vid)
        const edge = this.edgeMap.get(VPlanEdge.getEid(node, parent))
        node.outEdges.push(edge)
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
    const {padding, nodeWidth, nodeHeight, nodeWidthAlias} = conf.plan
    const {useOptAlias} = conf

    if (this.nodes.length === 0) {
      this.width = 30
      this.height = 15
      return
    }

    let g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir:'BT',
      ranksep: '10',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.nodes.forEach(node => {
      node.width = useOptAlias ? nodeWidthAlias : nodeWidth
      node.height = nodeHeight
      g.setNode(node.vid, node)
    })

    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        g.setEdge({v: edge.src.vid, w: edge.dst.vid})
      })
    })

    dagre.layout(g)

    // x, y is the center
    this.nodes.forEach(node => {
      node.x -= node.width / 2
      node.y -= node.height / 2
    })

    this.g = g
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        edge.points = g.edge({v: edge.src.vid, w: edge.dst.vid}).points
        edge.path = lineGen(edge.points)
      })
    })

    // if (this.plan.pid === 13 || this.plan.pid === 12) {
    //   console.log(this)
    // }
    // compute total size
    this.width = Math.max(...this.nodes.map(node => {
      return node.x + node.width
    })) + padding * 2
    this.height = Math.max(...this.nodes.map(node => {
      return node.y + node.height
    })) + padding * 2
  }
}

/**
 * @extends {Node<VPlanNode, VPlanEdge>}
 */
export class VPlanNode extends Node {
  /** @type {PlanNode} */
  planNode

  width
  height
  x
  y

  /** @type {['added' | 'to_remove']} */
  evoLabels = []

  constructor() {
    super()
  }

  get children() {
    return this.inEdges.map(e => e.src)
  }

  toString() {
    return this.planNode?.toString() ?? ""
  }

  toLimitedString(charLimit) {
    let str = this.toString()
    if (str.length > charLimit) {
      return str.slice(0, charLimit - 3) + '...'
    } else {
      return str
    }
  }

  getNodeName() {
    return this.isEmpty ? '' : this.planNode.name
  }

  getNodeId() {
    return this.isEmpty ? '' : this.planNode.vid
  }

  /**
   * @returns {'AR' | 'A' | 'R' | 'U'}
   */
  getEvoType() {
    // const added = this.evoLabels.includes('added')
    // const toRemove = this.evoLabels.includes('to_remove')
    // if (added && toRemove) {
    //   return 'AR'
    // } else if (added) {
    //   return 'A'
    // } else if (toRemove) {
    //   return 'R'
    // } else {
    //   return 'U'
    // }
    return 'U'
  }

  isAdded() {
    return this.evoLabels.includes('added')
  }

  toRemove() {
    return this.evoLabels.includes('to_remove')
  }
}

/**
 * @extends {Edge<VPlanNode, VPlanEdge>}
 */
export class VPlanEdge extends Edge {
  /** @type {PlanEdge} */
  planEdge

  /** @type {{x: int, y: int}[]} */
  points = []

  constructor() {
    super()
  }
}
