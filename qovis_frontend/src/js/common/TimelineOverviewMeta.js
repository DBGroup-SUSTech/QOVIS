import {getTextSize} from "@/utils/Layout"
import {getFadedColor} from "@/js/common"
import _ from "lodash"

export class TimelineOverviewMeta {
  /** @type {Plan[]} */
  plans = []
  /** @type {TOPhase[]} */
  phases = []

  height = 0
  width = 0

  /**
   * @param {Plan[]} plans
   * @param {[int, int][]} intervals
   * @param {int[]} impList
   * @returns {TimelineOverviewMeta}
   */
  init(plans, intervals, impList) {
    this.plans = plans
    this.phases = []
    const impSet = new Set(impList)

    intervals.forEach(([start, end], phaseIndex) => {
      let i = start === 0 ? 0 : start + 1

      let curGroup = []
      const planGroups = []
      const groupImpList = []
      const startList = [], endList = []
      let tmpStart = i

      for (; i <= end; i++) {
        if (impSet.has(i)) {
          // is important
          if (curGroup.length !== 0) {
            planGroups.push(curGroup)
            groupImpList.push(false)
            startList.push(tmpStart)
            endList.push(i - 1)
          }
          planGroups.push([plans[i]])
          groupImpList.push(true)
          startList.push(i)
          endList.push(i)
          tmpStart = i + 1

          curGroup = []
        } else {
          curGroup.push(plans[i])
        }
      }
      if (curGroup.length !== 0) {
        planGroups.push(curGroup)
        groupImpList.push(false)
        startList.push(tmpStart)
        endList.push(end)
      }

      const phase = new TOPhase()
      const items = planGroups.map((g, i) => {
        const start = startList[i], end = endList[i]
        const isImportant = groupImpList[i]
        return new TOItem().init(phase, plans.slice(start, end + 1), isImportant)
      })
      phase.init(this, items, phaseIndex)

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

export class TOPhase {
  /** @type {TimelineOverviewMeta} */
  toMeta
  /** @type {TOItem[]} */
  items = []
  /** @type {int} */
  phaseIndex = -1

  x
  y
  width
  height
  borderWidth

  /**
   * @param {TimelineOverviewMeta} toMeta
   * @param {TOItem[]} items
   * @param {int} phaseIndex
   * @returns {TOPhase}
   */
  init(toMeta, items, phaseIndex) {
    this.toMeta = toMeta
    this.items = items
    this.phaseIndex = phaseIndex
    return this
  }

  toString() {
    let phaseNames = _.flatten(this.items.map(it => it.plans))
        .map(p => p.meta.getPhaseName())
    phaseNames = _.uniq(phaseNames)
    if (phaseNames.length > 1) {
      console.log(phaseNames.join(','))
      _.remove(phaseNames, name => name === 'Transform' || name === 'Unknown')
    }
    return phaseNames.join(',')
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

export class TOItem {
  /** @type {TOPhase} */
  phase
  /** @type {Plan[]} */
  plans = []
  /** @type {bool} */
  isImportant

  x
  y
  width
  height
  rectWidth
  borderWidth

  init(phase, plans, isImportant) {
    this.phase = phase
    this.plans = plans
    this.isImportant = isImportant
    return this
  }

  toString() {
    if (this.isImportant) {
      return this.plans[0].meta.getSimpleName()
    } else {
      return `(${this.planCnt})`
    }
  }

  get planCnt() {
    return this.plans.length
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {itemPaddingY, itemPaddingX, itemBorderWidth, fontSize, collapseOffset} = conf.timelineOverviewItem

    const str = this.toString()
    const {height: textHeight, width: textWidth} = getTextSize(str, fontSize)

    this.rectWidth = this.width = textWidth + itemPaddingX * 2 + itemBorderWidth * 2
    if (this.planCnt === 0) {
      console.error("Empty timeline overview item", this)
    } else if (this.planCnt > 1) {
      this.width += (Math.min(this.planCnt, 4) - 1) * collapseOffset
    }

    this.height = textHeight + itemPaddingY * 2 + itemBorderWidth * 2
    this.borderWidth = itemBorderWidth
    // hardcode
    this.color = getFadedColor(this.plans[0].meta.type === 'soft trans' ? 'strategy' : this.plans[0].meta.type)
  }

  /**
   * @param {ConfigV1} conf
   */
  getCollapsedOffsets(conf) {
    const {collapseOffset} = conf.timelineOverviewItem
    const offsets = []
    for (let i = Math.min(this.planCnt, 4) - 1; i >= 0; i--) {
      offsets.push(collapseOffset * i)
    }
    return offsets
  }

  get collapseCnt() {
    return Math.min(this.planCnt, 4)
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
