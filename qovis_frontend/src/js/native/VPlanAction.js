import {getTextSize} from "@/utils/Layout"

export class VPlanAction {
  /** @type {Plan[]} */
  plans

  x
  y
  height
  width
  path

  /** @type {ActionItem[]} */
  actionItems = []

  /**
   * @param {Plan[]} plans
   */
  init(plans) {
    this.plans = plans
    this.actionItems = plans.map(p => {
      return (new ActionItem()).init(this, p)
    })
    return this
  }

  // getMetaType() {
  //   return this.plan.meta.type
  // }
  //
  // getChangeLabel() {
  //   return this.plan.meta.getSimpleName()
  // }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    this.actionItems.forEach(it => it.layout(conf))

    const {widthPlus, lengthPlus, arrowHeight, itemYPadding} = conf.arrow

    const arrowWidth = Math.max(...this.actionItems.map(it => it.width)) - lengthPlus

    this.path = `m0 ${widthPlus/2} l${arrowWidth} 0 ` + // -
        `l0 ${-widthPlus/2} l${lengthPlus} ${widthPlus/2+arrowHeight/2} ` +  // |\
        `l${-lengthPlus} ${widthPlus/2+arrowHeight/2} l0 ${-widthPlus/2} ` +   // |/
        `l${-arrowWidth} 0 Z`   // -

    // compute x y for action item
    let y = arrowHeight + widthPlus + itemYPadding
    this.actionItems.forEach(it => {
      it.x = 0
      it.y = y

      y += itemYPadding + it.height
    })

    // change all item width to max
    const maxItemWidth = Math.max(...this.actionItems.map(it => it.width))
    this.actionItems.forEach(it => it.width = maxItemWidth)

    // compute total size
    this.width = maxItemWidth
    this.height = Math.max(...this.actionItems.map(it => it.y + it.height))
  }
}

export class ActionItem {
  /** @type {VPlanAction} */
  vPlanAction
  /** @type {Plan} */
  plan

  x
  y
  textWidth
  /** @type {number} */
  width
  /** @type {number} */
  height

  init(vPlanAction, plan) {
    this.vPlanAction = vPlanAction
    this.plan = plan
    return this
  }

  getMetaType() {
    return this.plan.meta.type
  }

  getChangeLabel() {
    return this.plan.meta.getSimpleName()
  }

  layout(conf) {
    const {paddingX, paddingY} = conf.arrow

    const {width: textWidth, height: textHeight} = getTextSize(this.getChangeLabel(), 15)
    this.textWidth = textWidth
    this.width = textWidth + paddingX
    this.height = textHeight + paddingY * 2
  }
}
