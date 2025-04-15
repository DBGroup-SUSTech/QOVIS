import dagre from "dagre"
import * as d3 from "d3"


export class VisQueryPlan {
  /** @type {QueryPlan} */
  origin = null

  /** @type {VisPlanNode[]} */
  nodes = []
  /** @type {Map<int, VisPlanNode>} */
  nodeMap = new Map()

  /** @type {VisPlanEdge[]} */
  edges = []
  /** @type {Map<string, VisPlanEdge>} */
  edgeMap = new Map()

  // compute and update by outer object
  x
  y
  // compute by itself
  height
  width

  _beLayout = false

  /**
   * @param {QueryPlan} plan
   * @returns {this}
   */
  init(plan) {
    this.origin = plan

    this.nodes = []
    this.nodeMap = new Map()
    for (const v of plan.nodes) {
      const node = new VisPlanNode()
      node.init(v)
      this.nodes.push(node)
      this.nodeMap.set(node.vid, node)
    }
    for (const v of plan.nodes) {
      const node = this.nodeMap.get(v.vid)
      for (const c of v.children) {
        const child = this.nodeMap.get(c.vid)
        node.children.push(child)
      }
    }

    this.edges = []
    this.edgeMap = new Map()
    for (const p of this.nodes) {
      for (const c of p.children) {
        const edge = new VisPlanEdge()
        edge.init(p, c)
        this.edges.push(edge)
        this.edgeMap.set(edge.eid, edge)
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
      rankdir:'TB',
      ranksep: '10',
      nodesep: '15',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.nodes.forEach(node => {
      node.width = useOptAlias ? nodeWidthAlias : nodeWidth
      node.height = nodeHeight
      g.setNode(node.vid, node)
    })

    this.edges.forEach(edge => {
      g.setEdge({v: edge.src.vid, w: edge.dst.vid})
    })

    dagre.layout(g)

    // x, y given by dagre is the center
    this.nodes.forEach(node => {
      node.x -= node.width / 2
      node.y -= node.height / 2
    })

    this.g = g
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.edges.forEach(edge => {
      const e = g.edge({v: edge.src.vid, w: edge.dst.vid})
      edge.points = e.points
      edge.path = lineGen(edge.points)
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


export class VisPlanNode {
  /** @type {PlanNode} */
  origin = null

  /** @type {VisPlanNode[]} */
  children = []

  width
  height
  x
  y

  /** @type {['added' | 'to_remove']} */
  evoLabels = []

  /**
   * @param {PlanNode} node
   */
  init(node) {
    this.origin = node
    return this
  }

  get vid() {
    return this.origin.vid
  }

  get name() {
    return this.origin.name
  }

  toString() {
    return this.origin?.toString() ?? ""
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
    return this.origin.name
  }

  getNodeId() {
    return this.origin.vid
  }

  isAdded() {
    return this.evoLabels.includes('added')
  }

  toRemove() {
    return this.evoLabels.includes('to_remove')
  }

  get planNodeStr() {
    return this.origin.str
  }
}


export class VisPlanEdge {
  eid
  /** @type {VisPlanNode} */
  src
  /** @type {VisPlanNode} */
  dst

  /** @type {{x: int, y: int}[]} */
  points = []
  /** @type {string} */
  path = ""

  /**
   * @param {VisPlanNode} src
   * @param {VisPlanNode} dst
   */
  init(src, dst) {
    this.eid = VisPlanEdge.getEid(src, dst)
    this.src = src
    this.dst = dst
  }

  /**
   * @param {VisPlanNode} src
   * @param {VisPlanNode} dst
   * @returns {string}
   */
  static getEid(src, dst) {
    return `${src.vid}-${dst.vid}`
  }
}
