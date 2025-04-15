import {Graph, Node, Edge} from "@/js/common/Graph"
import dagre from "dagre"
import * as d3 from "d3"
import {getTextSize} from "@/utils/Layout"

/**
 * @extends {Graph<PlanStructNode, PlanStructEdge>}
 */
export class PlanStructure extends Graph {
  /** @type {SketchNode} */
  sketchNode
  /** @type {int} */
  index
  /** @type {Plan} */
  plan

  height
  width
  g

  get realPlanNodes() {
    return this.sketchNode.structureSeq[this.index]
  }

  init(sketchNode, index, plan) {
    this.sketchNode = sketchNode
    this.index = index
    this.plan = plan
    const realPlanNodes = this.realPlanNodes
    // console.log(realPlanNodes)

    const planNodeVid2psNode = new Map()
    realPlanNodes.forEach(planNode => {
      const node = this.addNode(new PlanStructNode())
      node.planNode = planNode
      planNodeVid2psNode.set(planNode.vid, node)
    })

    for (const node of [...this.nodes]) {
      node.planNode.providers.forEach(p => {
        let psNode = planNodeVid2psNode.get(p.vid)
        if (!psNode) {
          // create a virtual psNode, psNode -> node
          psNode = this.addNode(new PlanStructNode())
        }
        this.addEdge(new PlanStructEdge(), psNode, node)
      })
      node.planNode.consumers.forEach(c => {
        let psNode = planNodeVid2psNode.get(c.vid)
        if (!psNode) {
          // create a virtual psNode, node -> psNode
          psNode = this.addNode(new PlanStructNode())
          this.addEdge(new PlanStructEdge(), node, psNode)
        }
      })
    }
  }

  layout() {
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
      const {width, height} = node.toString() ?
          getTextSize(node.toString()) : {width: 5, height: 5}
      node.width = width + 2
      node.height = height + 2
      g.setNode(node.vid, node)
    })

    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        g.setEdge({v: edge.src.vid, w: edge.dst.vid})
      })
    })

    dagre.layout(g)

    this.g = g
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        edge.points = g.edge({v: edge.src.vid, w: edge.dst.vid}).points
        edge.path = lineGen(edge.points)
      })
    })

    // compute total size
    this.width = Math.max(...this.nodes.map(node => {
      return node.x + node.width / 2
    })) + 5 * 2
    this.height = Math.max(...this.nodes.map(node => {
      return node.y + node.height / 2
    })) + 5 * 2
  }
}

/**
 * @extends {Node<PlanStructNode, PlanStructEdge>}
 */
export class PlanStructNode extends Node {
  /** @type {PlanNode} */
  planNode = null

  x
  y
  width
  height

  get isFake() {
    return this.planNode == null
  }

  toString() {
    return this.planNode?.toString() ?? ""
  }

  toFullString() {
    return this.planNode?.str  ?? "FakeNode"
  }
}

/**
 * @extends {Edge<PlanStructNode, PlanStructEdge>}
 */
export class PlanStructEdge extends Edge {
  /** @type {[int, int][]} */
  points = []
}
