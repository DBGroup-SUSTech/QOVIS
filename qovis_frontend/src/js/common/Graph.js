import {IdCounter} from "@/utils/IdCounter"
import _ from 'lodash'

/**
 * @template V, E
 */
export class Node {
  /** @type {int} */
  vid
  /** @type {E[]} */
  inEdges
  /** @type {E[]} */
  outEdges

  init(vid) {
    this.vid = vid
    this.inEdges = []
    this.outEdges = []
  }
}

/**
 * @template V, E
 */
export class Edge {
  /** @type {string} */
  eid
  /** @type {V} */
  src
  /** @type {V} */
  dst

  /**
   * @param {V} src
   * @param {V} dst
   */
  init(src, dst) {
    this.eid = Edge.getEid(src, dst)
    this.src = src
    this.dst = dst
  }

  static getEid(src, dst) {
    return `${src.vid}-${dst.vid}`
  }
}

/**
 * @template V, E
 */
export class Graph {
  vidCounter = new IdCounter()

  /** @type {V[]} */
  nodes = []
  /** @type {E[]} */
  edges = []
  /** @type {Map<int, V>} */
  nodeMap = new Map()
  /** @type {Map<string, E>} */
  edgeMap = new Map()

  /**
   * @param {V} node
   * @returns {V}
   */
  addNode(node) {
    return this.addNodeWithVid(node, this.vidCounter.get())
  }

  addNodeWithVid(node, vid) {
    node.init(vid)
    this.nodes.push(node)
    this.nodeMap.set(node.vid, node)
    return node
  }

  updateIdCounter() {
    const maxId = Math.max(...this.nodes.map(v => v.vid))
    this.vidCounter.set(maxId)
  }

  deleteNode(vid) {
    const node = this.nodeMap.get(vid)
    for (const e of node.inEdges.concat(node.outEdges)) {
      this.deleteEdge(e.eid)
    }

    _.remove(this.nodes, node)
    this.nodeMap.delete(vid)

    return node
  }

  addEdge(edge, src, dst) {
    edge.init(src, dst)
    src.outEdges.push(edge)
    dst.inEdges.push(edge)

    this.edges.push(edge)
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
}
