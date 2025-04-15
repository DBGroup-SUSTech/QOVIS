
import {Node, Edge, Graph} from "@/js/common/Graph"
import {SketchEdgeSimpleMeta, SketchGraphSimpleMeta, SketchNodeSimpleMeta} from "@/js/timeline/SimpleMeta"

/**
 * @extends {Node<SketchNode, SketchEdge>}
 */
export class SketchNode extends Node {
  /** @type {string} */
  type = 'unknown'
  /** @type {PlanNode[][]} */
  structureSeq = []
  /** @type {boolean[]} */
  effList = []

  /** @type {SketchNodeSimpleMeta} */
  simpleMeta

  createSimpleMeta() {
    const meta = new SketchNodeSimpleMeta()
    meta.init(this)
    this.simpleMeta = meta
    return meta
  }
}

/**
 * @extends {Edge<SketchNode, SketchEdge>}
 */
export class SketchEdge extends Edge {
  /** @type {SketchEdgeSimpleMeta} */
  simpleMeta

  createSimpleMeta() {
    const meta = new SketchEdgeSimpleMeta()
    meta.init(this)
    this.simpleMeta = meta
    return meta
  }
}

/**
 * @extends {Graph<SketchNode, SketchEdge>}
 */
export class SketchGraph extends Graph {
  /** @type {int} */
  seqCnt
  /** @type {SketchGraphSimpleMeta} */
  simpleMeta

  createSimpleMeta(plans) {
    const meta = new SketchGraphSimpleMeta()
    meta.init(this, plans)
    this.simpleMeta = meta
    return meta
  }

  /**
   * @param obj
   * @param {Plan[]} plans
   * @returns {SketchGraph}
   */
  static load(obj, plans) {
    const sg = new SketchGraph()

    sg.seqCnt = obj.seqCnt

    for (const v of obj.nodes) {
      const node = sg.addNodeWithVid(new SketchNode(), v.vid)

      node.type = v.type
      node.structureSeq = v.structureSeq.map((s, i) => {
        const plan = plans[i]
        return s.map(planNodeId => plan.nodeMap.get(planNodeId))
      })
      node.effList = v.effList
    }

    sg.updateIdCounter()

    let maxVid = -1
    for (const node of sg.nodeMap.values()) {
      maxVid = Math.max(maxVid, node.vid)
    }
    sg.vidCounter.set(maxVid + 1)

    for (const e of obj.edges) {
      const src = sg.nodeMap.get(e.src)
      const dst = sg.nodeMap.get(e.dst)
      sg.addEdge(new SketchEdge(), src, dst)
    }

    return sg
  }
}
