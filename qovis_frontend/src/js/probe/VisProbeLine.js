import {TransType} from "@/js/probe/Transform"

export class VisProbeLine {
  /** @type {import('./ProbeLine.js').ProbeLine} */
  origin = null

  /** @type {VisQueryPlan[]} */
  plans = []
  /** @type {VisTransform[][]} */
  transforms = []

  width = 0
  height = 0

  /**
   * @param {ProbeLine} origin
   * @returns {VisProbeLine}
   */
  init(origin) {
    this.origin = origin
    this.plans = origin.plans.map(p => p.createVisObj())
    this.transforms = origin.transforms.map(lst => lst.map(t => t.createVisObj()))
    for (let i = 0; i < this.plans.length - 1; i++) {
      const vp0 = this.plans[i]
      const vp1 = this.plans[i + 1]
      const transformList = this.transforms[i]

      transformList.forEach(t => t.init(vp0, vp1))

      // hard code for add / remove
      transformList.forEach(t => {
        if (t.origin.type === TransType.INSERT) {
          vp1.nodeMap.get(t.origin.dstVid).evoLabels.push('added')
        } else if (t.origin.type === TransType.DELETE) {
          vp0.nodeMap.get(t.origin.srcVid).evoLabels.push('to_remove')
        }
      })
    }
    return this
  }

  /**
   * @param {ConfigV3} conf
   */
  layout(conf) {
    let curX = 0
    for (const plan of this.plans) {
      plan.layout(conf)
      plan.x = curX
      plan.y = 0
      curX += plan.width
    }
    this.width = curX
    this.height = Math.max(...this.plans.map(p => p.height))

    for (const transformList of this.transforms) {
      transformList.forEach(t => t.layout(conf))
    }
  }
}
