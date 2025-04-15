import {VPlanDag} from "@/js/native/VPlanDag"
import {VPlanAction} from "@/js/native/VPlanAction"
import _ from "lodash"

export class BatchGroup {
  /** @type {string} */
  batchName
  /** @type {Plan[]} */
  plans
  /** @type {VPlanDag[]} */
  planDags = []
  /** @type {VPlanAction[]} */
  planActions = []

  x
  y
  width
  height

  show = false

  /**
   * @param {Plan[]} plans
   * @return {BatchGroup}
   */
  init(plans) {
    this.batchName = plans[0].meta.batchName ?? ''
    this.plans = plans

    // compute group and create plan action to each group

    const getNodeIdList = (plan) => {
      return Array.from(plan.nodeMap.values()).map(node => node.vid)
    }
    const  /** @type {Plan[][]} */ groups = []
    let group = [plans[0]]
    let addVidList = []
    for (let i = 1; i < plans.length; i++) {
      const p0 = plans[i - 1], p1 = plans[i]
      const list0 = getNodeIdList(p0), list1 = getNodeIdList(p1)
      const removed = _.difference(list0, list1)
      if (_.intersection(removed, addVidList).length !== 0) {
        // can't put plan[i] into previous group
        groups.push(group)
        group = [p1]
        addVidList = []
      } else {
        // can be merged into one group
        group.push(p1)
        const added = _.difference(list1, list0)
        addVidList.push(...added)
      }
    }
    if (group.length !== 0) {
      groups.push(group)
    }

    this.planDags = []
    groups.forEach(group => {
      this.planDags.push((new VPlanDag()).init(group[0]))
      if (group.length === 1) {
        return
      }
      this.planDags.push((new VPlanDag()).init(group[group.length - 1]))
    })

    this.planActions = []
    groups.forEach((group, i) => {
      if (i !== 0) {
        // also create an action
        const act = (new VPlanAction()).init([group[0]])
        this.planActions.push(act)
      }
      if (group.length === 1) {
        return
      }
      const act = (new VPlanAction()).init(group.slice(1, group.length))
      this.planActions.push(act)
    })

    // this.planActions = plans.slice(1, plans.length).map(p => (new VPlanAction()).init([p]))

    // compute evo types for plan node
    for (let i = 0; i < this.planDags.length - 1; i++) {
      const dag0 = this.planDags[i], dag1 = this.planDags[i + 1]
      const vidList0 = dag0.nodes.map(node => node.vid)
      const vidList1 = dag1.nodes.map(node => node.vid)

      const added = _.difference(vidList1, vidList0)
      for (const vid of added) {
        dag1.nodeMap.get(vid).evoLabels.push('added')
      }

      const toRemove = _.difference(vidList0, vidList1)
      for (const vid of toRemove) {
        dag0.nodeMap.get(vid).evoLabels.push('to_remove')
      }
    }

    // compute evo type for plan node for one action
    // for (let i = 0; i < this.planDags.length - 1; i++) {
    //   const dag0 = this.planDags[i], dag1 = this.planDags[i + 1]
    //   const vidList0 = dag0.nodes.map(node => node.vid)
    //   const vidList1 = dag1.nodes.map(node => node.vid)
    //
    //   const added = _.difference(vidList1, vidList0)
    //   for (const vid of added) {
    //     dag1.nodeMap.get(vid).evoLabels.push('added')
    //   }
    //
    //   const toRemove = _.difference(vidList0, vidList1)
    //   for (const vid of toRemove) {
    //     dag0.nodeMap.get(vid).evoLabels.push('to_remove')
    //   }
    // }

    return this
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {phasePaddingX, phasePaddingY, itemPadding} = conf.phaseGroup

    this.planDags.forEach(p => p.layout(conf))
    this.planActions.forEach(a => a.layout(conf))

    this.height = Math.max(
        0,
        ...this.planDags.map(p => p.height),
        ...this.planActions.map(a => a.height)
    ) + phasePaddingY * 2 + 50

    let curX = phasePaddingX
    for (let i = 0; i < this.planDags.length; i++) {
      const p = this.planDags[i]
      p.x = curX
      p.y = (this.height - p.height) / 2
      curX += p.width + itemPadding

      if (i !== this.planDags.length - 1) {
        const a = this.planActions[i]
        a.x = curX + itemPadding
        a.y = (this.height - a.height) / 2
        curX += a.width + itemPadding
      }
    }

    this.width = curX + 20
  }
}
