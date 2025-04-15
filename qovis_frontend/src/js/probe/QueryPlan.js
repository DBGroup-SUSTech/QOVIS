import {VisQueryPlan, VisPlanNode} from "@/js/probe/VisQueryPlan"

export class QueryPlan {
  /** @type {int} */
  pid
  /** @type {PlanNode} */
  root = null
  /** @type {PlanNode[]} */
  nodes = []
  /** @type {Map<int, PlanNode>} */
  nodeMap = new Map()

  /** @type {VisQueryPlan} */
  visObj = null

  init(json) {
    this.pid = json.pid
    this.nodes = json.nodes.map(n => new PlanNode().init(n))
    this.nodeMap = new Map(this.nodes.map(n => [n.vid, n]))
    for (const u of json.nodes) {
      this.nodeMap.get(u.vid).children = u.children.map(vid => this.nodeMap.get(vid))
    }
    this.root = this.nodes.find(n => n.vid === json.root)
    return this
  }

  createVisObj() {
    this.visObj = new VisQueryPlan().init(this)
    return this.visObj
  }
}

export class PlanNode {
  vid
  name
  str
  clazz
  /** @type {PlanNode[]} */
  children = []

  visObj = null

  init({vid, name, clazz, str}) {
    this.vid = vid
    this.name = name
    this.str = str
    this.clazz = clazz
    return this
  }

  createVisObj() {
    this.visObj = new VisPlanNode().init(this)
    return this.visObj
  }
}

