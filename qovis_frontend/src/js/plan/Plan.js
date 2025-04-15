import {Meta} from "@/js/plan/Meta"

export class PlanNode {
  name
  vid
  str
  addr
  planLater
  evoLabels

  /** @type {PlanNode[]} */
  providers
  /** @type {PlanNode[]} */
  consumers

  constructor(name, vid, str, addr, planLater, evoLabels) {
    this.providers = []
    this.consumers = []

    this.name = name
    this.vid = vid
    this.str = str
    this.addr = addr
    this.planLater = planLater
    this.evoLabels = evoLabels
  }

  toAlias(alias) {
    // const mark = this.planLater !== null ? "'" : ""
    // return `${alias}#${this.vid}${mark}`
    return `${alias}#${this.vid}`
  }

  toString() {
    // const mark = this.planLater !== null ? "'" : ""
    // return `${this.name}#${this.vid}${mark}`
    return `${this.name}#${this.vid}`
  }
}

export class PlanEdge {
  eid
  /** @type {PlanNode} */
  provider
  /** @type {PlanNode} */
  consumer

  constructor(provider, consumer) {
    this.eid = PlanEdge.getEid(provider, consumer)
    this.provider = provider
    this.consumer = consumer
  }

  static getEid(provider, consumer) {
    return `${provider.vid}-${consumer.vid}`
  }

  toString() {
    return this.provider.toString() + '->' + this.consumer.toString()
  }
}

export class Plan {
  /** @type {int} */
  pid
  /** @type {Meta} */
  meta
  /** @type {PlanNode} */
  root
  /** @type {Map<int, PlanNode>} */
  nodeMap
  /** @type {Map<string, PlanEdge>} */
  edgeMap
  /** @type {Object[]} */
  infoList

  constructor(pid) {
    this.pid = pid
    this.nodeMap = new Map()
    this.edgeMap = new Map()
  }

  static load(obj) {
    const plan = new Plan(obj.pid)
    plan.meta = obj.meta ? Meta.load(obj.meta) : null

    for (const v of obj.nodes) {
      const node = new PlanNode(v.name, v.vid, v.str, v.addr, v.planLater, v.evoLabels)
      plan.nodeMap.set(node.vid, node)
    }

    for (const e of obj.edges) {
      const p = plan.nodeMap.get(e.pVid)
      const c = plan.nodeMap.get(e.cVid)
      const edge = new PlanEdge(p, c)
      plan.edgeMap.set(edge.eid, edge)
    }

    for (const v of obj.nodes) {
      const node = plan.nodeMap.get(v.vid)
      if (this.pid === 48) {
        console.log(this, obj, v)
      }
      v.pros.forEach(vid => node.providers.push(plan.nodeMap.get(vid)))
      v.cons.forEach(vid => node.consumers.push(plan.nodeMap.get(vid)))
    }

    plan.root = plan.nodeMap.get(obj.root)

    const infoList = []
    // console.log('>>>', obj.infoList)
    for (const info of obj.infoList) {
      const item = {}
      for (const [k, v] of Object.entries(info)) {
        if (['plan', 'logicalPlan', 'physicalPlan'].includes(k)) {
          item[k] = Plan.load(v)
        } else if (['stages'].includes(k)) {
          item[k] = v.map(w => Plan.load(w))
        } else {
          item[k] = v
        }
      }
      infoList.push(item)
    }
    plan.infoList = infoList

    return plan
  }
}
