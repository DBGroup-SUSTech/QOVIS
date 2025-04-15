import {PlanStructure} from "@/js/timeline/PlanStructure"
import _ from 'lodash'

export class TimelineRow {
  /** @type {SketchNode} */
  sketchNode
  /** @type {TimelineItem[]} */
  timelineItems = []

  /** @type {number} */
  height = 0

  /**
   * @param {SketchNode} node
   * @param {Plan[]} plans
   */
  init(node, plans) {
    this.sketchNode = node

    this.timelineItems = []

    this.sketchNode.effList.forEach(isEff => {
      const item = new TimelineItem()
      item.isEff = isEff
      this.timelineItems.push(item)
    })

    this.timelineItems.forEach((item, index) => {
      const structure = new PlanStructure()
      structure.init(node, index, plans[index])
      item.structure = structure
    })

    this.timelineItems[0].step = Step.createStartStep()
    let lastEffIndex = 0
    for (let i = 1; i < this.timelineItems.length; i++) {
      const item = this.timelineItems[i]
      if (!item.isEff) {
        continue
      }

      const step = new Step()
      step.start = lastEffIndex
      step.end = i
      step.labels = plans.slice(step.start + 1, step.end + 1)
          .map(p => p.meta.name)
      item.step = step

      lastEffIndex = i
    }

    // console.log(this.timelineItems)
  }

  layout() {
    this.timelineItems.forEach(item => item.layout())
    this.height = _.max(this.timelineItems.map(o => o.height))
  }
}

export class TimelineItem {
  /** @type {boolean} */
  isEff
  /** @type {Step} */
  step
  /** @type {PlanStructure} */
  structure

  width
  alignWidth
  height

  getLastMeta() {
    return this.structure.plan.meta
  }

  layout() {
    if (this.isEff) {
      this.structure.layout()
      this.width = this.structure.width
      this.alignWidth = this.structure.width
      this.height = this.structure.height
    } else {
      this.width = 0
      this.alignWidth = 0
      this.height = 10
    }
  }
}

export class Step {
  /** @type {int} Not included */
  start
  /** @type {int} included */
  end
  /** @type {string[]} */
  labels = []

  static createStartStep() {
    const ret = new Step()
    ret.start = -1
    ret.end = 0
    ret.labels = ['Start']
    return ret
  }

  getUniqueOrderedLabels() {
    const labels = []
    if (this.labels.length === 0) {
      return labels
    }
    labels.push(this.labels[0])
    for (let i = 1; i < this.labels.length; i++) {
      if (this.labels[i - 1] !== this.labels[i]) {
        labels.push(this.labels[i])
      }
    }
    return labels
  }

  getLastLabel() {
    return _.last(this.labels)
  }

  toString() {
    // return this.getUniqueOrderedLabels().join(',')
    return this.getLastLabel()
  }
}
