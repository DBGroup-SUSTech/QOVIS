import {QueryPlan} from "@/js/probe/QueryPlan"
import {Transform} from "@/js/probe/Transform"
import {VisProbeLine} from "@/js/probe/VisProbeLine"


export class ProbeLine {
  gValue = 0
  hValue = 0
  /** @type {QueryPlan[]} */
  plans = []
  /** @type {string[]} */
  rules = []
  /** @type {Transform[]} */
  transforms = []

  visObj = null

  createVisObj() {
    this.visObj = new VisProbeLine().init(this)
    return this.visObj
  }

  init(src, dst, [g, h, plan, rules, transforms]) {
    this.gValue = g
    this.hValue = h
    this.plans = [
        new QueryPlan().init(src),
        new QueryPlan().init(plan),
        new QueryPlan().init(dst),
    ]
    this.rules = rules
    this.transforms = transforms.map(lst => lst.map(t => Transform.load(t)))
    return this
  }
}
