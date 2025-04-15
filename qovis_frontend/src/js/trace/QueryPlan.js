import {VisQueryPlan} from "@/js/trace/VisQueryPlan"
import {PlanNode} from "@/js/trace/PlanNode"

export class QueryPlan {
  /** @type {int} */
  pid
  /** @type {PlanNode} */
  root
  /** @type {PlanNode[]} */
  nodes
  /** @type {Map<int, PlanNode>} */
  nodeMap
  /** @type {string[]} */
  labels
  /** @type {boolean} */
  resolved

  /** @type {VisQueryPlan} */
  visObj = null

  init({pid, root, nodes, labels, resolved}) {
    this.pid = pid

    this.nodes = []
    this.nodeMap = new Map()
    for (const v of nodes) {
      const node = new PlanNode(v.name, v.clazz, v.vid, v.str, v.addr, v.params, this)
      this.nodes.push(node)
      this.nodeMap.set(node.vid, node)
    }

    // build tree structure
    for (const u of nodes) {
      const parent = this.nodeMap.get(u.vid)
      for (const childId of u.children) {
        const child = this.nodeMap.get(childId)
        child.parent = parent
        parent.children.push(child)
      }
    }

    this.root = this.nodeMap.get(root)

    this.labels = labels
    this.resolved = resolved

    return this
  }

  /**
   * @returns {VisQueryPlan}
   */
  createVisObj() {
    this.visObj = new VisQueryPlan().init(this)
    return this.visObj
  }
}
