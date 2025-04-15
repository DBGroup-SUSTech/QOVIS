import {getTextSize} from "@/utils/Layout"

export class VisTran {
  /** @type {Plan} */
  plan

  x
  y
  height
  width
  path

  /**
   * @param {Plan} plan
   */
  init(plan) {
    this.plan = plan
    return this
  }

  getMetaType() {
    return this.plan.meta.type
  }

  getChangeLabel() {
    let name = this.plan.meta.name
    if (name.endsWith("$")) {
      name = name.substring(0, name.length - 1)
    }
    if (name.includes('.')) {
      name = name.split('.')[1]
    }
    if (name.includes("$")) {
      name = name.split("$")[1]
    }
    return name
  }

  layout(conf) {
    const {widthPlus, lengthPlus, paddingX, paddingY} = conf.arrow

    const {width: textWidth, height: textHeight} = getTextSize(this.getChangeLabel(), 15)
    const boxWidth = textWidth + paddingX,
          boxHeight = textHeight + paddingY * 2

    this.path = `m0 ${widthPlus/2} l${boxWidth} 0 ` + // -
        `l0 ${-widthPlus/2} l${lengthPlus} ${widthPlus/2+boxHeight/2} ` +  // |\
        `l${-lengthPlus} ${widthPlus/2+boxHeight/2} l0 ${-widthPlus/2} ` +   // |/
        `l${-boxWidth} 0 Z`   // -

    // compute total size
    this.width = boxWidth + lengthPlus
    this.height = boxHeight + widthPlus
  }
}
