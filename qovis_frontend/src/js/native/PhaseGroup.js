import {VPlanDag} from "@/js/native/VPlanDag"
import {VPlanAction} from "@/js/native/VPlanAction"
import _ from "lodash"
import {BatchGroup} from "@/js/native/BatchGroup"
// import {LzwAlgo} from "@/js/algo/Lzw"

export class PhaseGroup {
  /** @type {string} */
  phaseName
  /** @type {Plan[]} */
  plans
  /** @type {BatchGroup[]} */
  batchGroups

  x
  y
  width
  height

  show = false

  /**
   * @param {string} phaseName
   * @param {Plan[]} plans
   * @return {PhaseGroup}
   */
  init(phaseName, plans) {
    this.phaseName = phaseName
    this.plans = plans

    // first run lzw to get the groups
    // const actions = plans.map(p => p.meta.name).slice(1)
    // const presets = actions.map(a => [a])
    // const a = ['CollapseProject', 'RemoveNoopOperators', 'PushDownLeftSemiAntiJoin', 'ColumnPruning']
    // for (let i = 2; i <= 4; i++) {
    //   presets.push(a.slice(0, i))
    // }
    // const lzw = new LzwAlgo(presets, 10)
    // const compressed = lzw.compress(actions)
    // const dict = lzw.parsedDictionary
    // console.log({compressed, dict})

    // merge plans by batch
    const batches = []
    let batch = [plans[0]]
    const getBatchId = (index) => {
      const plan = plans[index]
      if (plan.meta.metaType === 'softTrans' && index < plans.length - 1) {
        return getBatchId(index + 1)
      } else {
        return plan.meta.batchId ?? ''
      }
    }
    for (let i = 1; i < plans.length; i++) {
      const p1 = plans[i]
      if (getBatchId(i - 1) === getBatchId(i)) {
        batch.push(p1)
      } else {
        batches.push(batch)
        batch = [p1]
      }
    }
    if (batch.length !== 0) {
      batches.push(batch)
    }
    this.batches = batches

    this.batchGroups = this.batches.map(batch => (new BatchGroup()).init(batch))

    return this
  }

  get isSingleBatch() {
    return this.batchGroups.length === 1
  }

  /**
   * @param {Plan[]} plans
   * @return {{planDags: VPlanDag[], planActions: VPlanAction[]}}}
   */
  mergePlans(plans) {
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

    const planDags = []
    groups.forEach(group => {
      planDags.push((new VPlanDag()).init(group[0]))
      if (group.length === 1) {
        return
      }
      planDags.push((new VPlanDag()).init(group[group.length - 1]))
    })

    const planActions = []
    groups.forEach((group, i) => {
      if (i !== 0) {
        // also create an action
        const act = (new VPlanAction()).init([group[0]])
        planActions.push(act)
      }
      if (group.length === 1) {
        return
      }
      const act = (new VPlanAction()).init(group.slice(1, group.length))
      planActions.push(act)
    })

    return {planDags, planActions}
  }

  /**
   * @param {ConfigV1} conf
   */
  layout(conf) {
    const {phasePaddingX, phasePaddingY, batchTextHeight} = conf.phaseGroup

    this.batchGroups.forEach(group => group.layout(conf))

    this.height = Math.max(...this.batchGroups.map(group => group.height)) + phasePaddingY * 2 + 40

    if (this.isSingleBatch) {
      const group = this.batchGroups[0]
      group.x = phasePaddingX
      group.y = (this.height - group.height) / 2
      this.width = group.width + phasePaddingX + 40

    } else {
      this.height += batchTextHeight

      let curX = phasePaddingX
      for (let i = 0; i < this.batchGroups.length; i++) {
        const group = this.batchGroups[i]
        group.x = curX
        group.y = (this.height - group.height) / 2 + batchTextHeight
        curX += group.width + phasePaddingX
      }
      this.width = curX + 40
    }

    this.x = 0
    this.y = 0

  }
}
