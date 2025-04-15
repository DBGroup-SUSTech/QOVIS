import {getTextSize} from "@/utils/Layout"
import {getFadedColor} from "@/js/common"

export class OverviewTrace {
  /** @type {Plan[]} */
  plans = []
  /** @type {OverviewPhase[]} */
  phases = []

  height = 0
  width = 0

  /**
   * @param {Plan[]} plans
   * @param {[int, int][]} intervals
   * @param {string[]} phaseNames
   * @returns {OverviewTrace}
   */
  init(plans, intervals, phaseNames) {
    this.plans = plans
    this.phases = []

    intervals.forEach(([start, end], phaseIndex) => {
      const planGroup = plans.slice(start + 1, end)   // first two plan has same meta

      const phase = new OverviewPhase()
      const items = planGroup.map(p => {
        return new OverviewItem().init(phase, p, true)
      })
      phase.init(phaseNames[phaseIndex], this, items, phaseIndex)

      this.phases.push(phase)
    })

    return this
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {paddingX, paddingY, phaseGap} = conf.timelineOverviewItem

    let x = paddingX
    let phaseHeight = 0
    this.phases.forEach(phase => {
      phase.layout(conf)
      phase.x = x
      phase.y = paddingY
      x += phase.width + phaseGap
      phaseHeight = Math.max(phaseHeight, phase.height)
    })

    this.width = x - phaseGap + paddingX
    this.height = paddingY * 2 + phaseHeight
  }
}

export class OverviewPhase {
  /** @type {string} */
  phaseName
  /** @type {OverviewTrace} */
  overviewTrace
  /** @type {OverviewItem[]} */
  items = []
  /** @type {int} */
  phaseIndex = -1

  x
  y
  width
  height
  borderWidth

  /**
   * @param {string} phaseName
   * @param {OverviewTrace} overviewTrace
   * @param {OverviewItem[]} items
   * @param {int} phaseIndex
   * @returns {OverviewPhase}
   */
  init(phaseName, overviewTrace, items, phaseIndex) {
    this.phaseName = phaseName
    this.overviewTrace = overviewTrace
    this.items = items
    this.phaseIndex = phaseIndex
    return this
  }

  toString() {
    // let phaseNames = this.items.map(it => it.plan)
    //     .map(p => p.meta.getPhaseName())
    // phaseNames = _.uniq(phaseNames)
    // if (phaseNames.length > 1) {
    //   console.log(phaseNames.join(','))
    //   _.remove(phaseNames, name => name === 'Transform' || name === 'Unknown')
    // }
    // return phaseNames.join(',')
    return this.phaseName
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {phasePaddingX, phasePaddingTop, phasePaddingBottom,
      phaseGap, phaseBorderWidth} = conf.timelineOverviewItem

    let x = phasePaddingX
    let itemHeight = 0
    this.items.forEach(item => {
      item.layout(conf)
      item.x = x
      item.y = phasePaddingTop
      x += item.width + phaseGap
      itemHeight = Math.max(itemHeight, item.height)
    })

    this.width = x - phaseGap + phasePaddingX
    this.height = phasePaddingTop + phasePaddingBottom + itemHeight
    this.borderWidth = phaseBorderWidth
  }

  /**
   * @param {ConfigV1} conf
   */
  getTextX(conf) {
    const {phasePaddingX, phaseBorderWidth} = conf.timelineOverviewItem
    return phasePaddingX + phaseBorderWidth
  }

  /**
   * @param {ConfigV1} conf
   */
  getTextY(conf) {
    const {fontSize, phaseBorderWidth} = conf.timelineOverviewItem
    return 4 + fontSize + phaseBorderWidth
  }
}

export class OverviewItem {
  /** @type {TOPhase} */
  phase
  /** @type {Plan} */
  plan
  /** @type {bool} */
  isImportant

  x
  y
  width
  height
  borderWidth
  color

  init(phase, plan, isImportant) {
    this.phase = phase
    this.plan = plan
    this.isImportant = isImportant
    return this
  }

  toString() {
    if (this.isImportant) {
      return this.plan.meta.getSimpleName()
    } else {
      return ""
    }
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {itemPaddingY, itemPaddingX, itemBorderWidth, fontSize} = conf.timelineOverviewItem

    const str = this.toString()
    const {height: textHeight, width: textWidth} = getTextSize(str, fontSize)

    this.width = textWidth + itemPaddingX * 2 + itemBorderWidth * 2

    this.height = textHeight + itemPaddingY * 2 + itemBorderWidth * 2
    this.borderWidth = itemBorderWidth

    this.color = getFadedColor(this.plan.meta.type)
  }

  /**
   * @param {ConfigV1} conf
   */
  getTextX(conf) {
    const {itemPaddingX, itemBorderWidth} = conf.timelineOverviewItem
    return itemPaddingX + itemBorderWidth
  }

  /**
   * @param {ConfigV1} conf
   */
  getTextY(conf) {
    const {itemPaddingY, fontSize, itemBorderWidth} = conf.timelineOverviewItem
    return itemPaddingY + fontSize + itemBorderWidth
  }
}
