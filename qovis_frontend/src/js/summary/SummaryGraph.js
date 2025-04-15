import {IdCounter} from "@/utils/IdCounter"
import _ from 'lodash'
import {Plan} from "@/js/plan/Plan"

export class SNode {
  vid
  /** @type {SEdge[]} */
  inEdges
  /** @type {SEdge[]} */
  outEdges
  /** @type {PlanNode[]} */
  planNodes

  constructor(vid) {
    this.vid = vid
    this.inEdges = []
    this.outEdges = []
    this.planNodes = []
  }
}

export class SEdge {
  eid
  /** @type {SNode} */
  src
  /** @type {SNode} */
  dst

  constructor(src, dst) {
    this.eid = SEdge.getEid(src, dst)
    this.src = src
    this.dst = dst
  }

  static getEid(src, dst) {
    return `${src.vid}-${dst.vid}`
  }
}

export class SGraph {
  vidCounter = new IdCounter()
  /** @type {Map<int, SNode>} */
  nodeMap = new Map()
  /** @type {Map<string, SEdge>} */
  edgeMap = new Map()
  /** @type {Plan} */
  plan

  addNode() {
    return this.addNodeWithVid(this.vidCounter.get())
  }

  addNodeWithVid(vid) {
    const node = new SNode(vid)
    this.nodeMap.set(node.vid, node)
    return node
  }

  deleteNode(vid) {
    const node = this.nodeMap.get(vid)
    for (const e of node.inEdges.concat(node.outEdges)) {
      this.deleteEdge(e.eid)
    }
    this.nodeMap.delete(vid)
    return node
  }

  /**
   * @param {SNode} src
   * @param {SNode} dst
   */
  addEdge(src, dst) {
    const edge = new SEdge(src, dst)
    src.outEdges.push(edge)
    dst.inEdges.push(edge)
    this.edgeMap.set(edge.eid, edge)
    return edge
  }

  deleteEdge(eid) {
    const edge = this.edgeMap.get(eid)
    _.remove(edge.src.outEdges, edge)
    _.remove(edge.dst.inEdges, edge)
    this.edgeMap.delete(eid)
    return edge
  }

  static load(obj) {
    const sg = new SGraph()

    sg.plan = Plan.load(obj.plan)

    for (const v of obj.nodes) {
      const node = new SNode(v.vid)
      const planNodes = []
      for (let i = 0; i < v.planNodes.length; i++) {
        const planNode = v.planNodes[i]     // vid
        planNodes.push(sg.plan.nodeMap.get(planNode))
      }
      node.planNodes = planNodes
      sg.nodeMap.set(node.vid, node)
    }

    let maxVid = -1
    for (const node of sg.nodeMap.values()) {
      maxVid = Math.max(maxVid, node.vid)
    }
    sg.vidCounter.set(maxVid + 1)

    for (const e of obj.edges) {
      const src = sg.nodeMap.get(e.src)
      const dst = sg.nodeMap.get(e.dst)
      sg.addEdge(src, dst)
    }

    return sg
  }
}
