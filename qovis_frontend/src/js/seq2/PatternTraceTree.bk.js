// import assert from "assert"
// import * as d3 from "d3"
// import {VPlanDag} from "@/js/native/VPlanDag"
// import _ from "lodash"
//
// /**
//  * @enum {string}
//  * @readonly
//  */
// export const NodeType = {
//   ROOT: 'root',
//   PHASE_PATTERN: 'phase_pattern',
//   PHASE: 'phase',
//   BATCH_PATTERN: 'batch_pattern',
//   BATCH: 'batch',
//   ACTION_PATTERN: 'action_pattern',
//   ACTION: 'action',
// }
//
// export class PatternTraceTree2 {
//   /** @type {PatternTraceNode2} */
//   root = new PatternTraceNode2(NodeType.ROOT)
//   /** @type {PlanBlock[]} */
//   planBlocks = []
//
//   /** @type {Map<string, number>} */
//   colorMap = new Map()
//   color = d3.scaleOrdinal(d3.schemeCategory10.concat(d3.schemeAccent))
//   sizeScale = d3.scaleLinear()
//
//   /** @type {Map<string, Pattern>} */
//   patternMap = new Map()
//
//   /** @type {PatternTraceNode2[]} */
//   selectedNodes = []
//   /** @type {(VPlanDag | null)[]} */
//   vPlanDags = []    // size of this = size of selectedNodes + 1. this is a cache for all vPlanDags
//   /** @type {Plan[]} */
//   plans = []
//
//   // layout
//   width = 0
//   height = 0
//   startX = 0
//   startY = 0
//
//   maxLevel = 0
//   planDagStartY = 0
//
//   /**
//    * @param {ConfigV3} config
//    * @param {DynamicGraph} dg
//    * @param {Pattern[]} patterns
//    */
//   // eslint-disable-next-line no-unused-vars
//   constructor(config, dg, patterns) {
//     this.plans = dg.plans
//     this.selectedNodes = []
//     this.vPlanDags = this.plans.map(() => null)
//
//     const phaseIntervals = dg.phaseIntervals
//     const phaseNames = dg.phaseNames.map(name => {
//       if (name.includes('#')) {
//         return name.split('#')[0]
//       } else {
//         return name
//       }
//     })
//
//     // const patternMap = this.patternMap = new Map()
//     // for (const pattern of patterns) {
//     //   patternMap.set(pattern.name, pattern)
//     // }
//
//     // init root
//     this.root.init(this, null, 'root', 0, this.plans.length)
//     this.root.setExpanded(true)
//
//     const matchGroups1 = this.matchPattern(phaseNames)
//
//     console.log('>>>1')
//     // eslint-disable-next-line no-constant-condition
//     // if (true) return
//
//     const tmpPhaseIntervals = [...phaseIntervals]
//     const tmpPhaseNames = [...phaseNames]
//     for (let i = 0; i < matchGroups1.length; i++) {
//       const phasePatternNode = new PatternTraceNode2(NodeType.PHASE_PATTERN)
//       const group = matchGroups1[i]
//       const intervals = tmpPhaseIntervals.splice(0, group.length)
//
//       console.log('>>>', i, matchGroups1, group)
//       // eslint-disable-next-line no-constant-condition
//       if (i >= 2) return
//
//       const startIdx = intervals[0][0], endIdx = intervals[group.length - 1][1]
//       phasePatternNode.init(this, this.root, tmpPhaseNames[0], startIdx, endIdx)
//       this.root.children.push(phasePatternNode)
//
//
//       // for (let j = 0; j < group.length; j++) {
//       //   const [start, end] = intervals[j]
//       //   const phaseName = tmpPhaseNames.shift()
//       //
//       //   const phaseNode = new PatternTraceNode2(NodeType.PHASE)
//       //   phaseNode.init(this, phasePatternNode, phaseName, start, end)
//       //   phasePatternNode.children.push(phaseNode)
//       // }
//
//     }
//
//
//     // assert(tmpPhaseIntervals.length === 0, `tmpPhaseIntervals.length !== 0: ${tmpPhaseIntervals}`)
//     // assert(tmpPhaseNames.length === 0, `tmpPhaseNames.length !== 0: ${tmpPhaseNames}`)
//
//     for (const phasePatternNode of this.root.children) {
//       for (const phaseNode of phasePatternNode.children) {
//         const phasePlans = phaseNode.getPlans().splice(1)
//
//         // split phase plans to batch
//
//         const batchPlansList = []
//         let batchPlans = [phasePlans[0]]
//         const getBatchId = (index) => {
//           const plan = phasePlans[index]
//           if (plan.meta.batchId == null && index < phasePlans.length - 1) {
//             return getBatchId(index + 1)
//           } else {
//             return plan.meta.batchId ?? ''
//           }
//         }
//         for (let i = 1; i < phasePlans.length; i++) {
//           const p1 = phasePlans[i]
//           if (getBatchId(i - 1) === getBatchId(i)) {
//             batchPlans.push(p1)
//           } else {
//             batchPlansList.push(batchPlans)
//             batchPlans = [p1]
//           }
//         }
//         if (batchPlans.length !== 0) {
//           batchPlansList.push(batchPlans)
//         }
//
//         const batchNames = batchPlansList.map(batchPlans => this.inferBatchName(batchPlans))
//
//         const matchGroups2 = this.matchPattern(batchNames)
//
//         const tmpBatchPlansList = [...batchPlansList]
//         const tmpBatchNames = [...batchNames]
//         let startIdx1 = phaseNode.startIdx
//         for (let i = 0; i < matchGroups2.length; i++) {
//           const batchPatternNode = new PatternTraceNode2(NodeType.BATCH_PATTERN)
//           const group = matchGroups2[i]
//           const groupBatchPlans = tmpBatchPlansList.splice(0, group.length)
//           const tmpPlans = groupBatchPlans.flat()
//           batchPatternNode.init(this, phaseNode, tmpBatchNames[0],
//               startIdx1, startIdx1 + tmpPlans.length)
//           phaseNode.children.push(batchPatternNode)
//
//           for (let j = 0; j < group.length; j++) {
//             const planSlice = groupBatchPlans[j]
//             const batchName = tmpBatchNames.shift()
//
//             const batchNode = new PatternTraceNode2(NodeType.BATCH)
//             batchNode.init(this, batchPatternNode, batchName, startIdx1, startIdx1 + planSlice.length)
//             batchPatternNode.children.push(batchNode)
//
//             startIdx1 += planSlice.length
//           }
//         }
//         // assert(startIdx1 === phaseNode.endIdx, `phase plan check failed: ${phaseNode.name} ${startIdx1} ${phaseNode.endIdx}`)
//         // assert(tmpBatchPlansList.length === 0, `tmpBatchPlansList.length !== 0: ${tmpBatchPlansList}`)
//         // assert(tmpBatchNames.length === 0, `tmpBatchNames.length !== 0: ${tmpBatchNames}`)
//
//         for (const batchPatternNode of phaseNode.children) {
//           for (const batchNode of batchPatternNode.children) {
//             const batchPlans = batchNode.getPlans().splice(1)   // because the first plan stores the meta of last update
//             const actionNames = batchPlans.map(p => p.meta.getSimpleName())
//
//             const matchGroups3 = this.matchPattern(actionNames)
//
//             const tmpPlans = [...batchPlans]
//             const tmpNames = [...actionNames]
//             let startIdx2 = batchNode.startIdx
//             for (let i = 0; i < matchGroups3.length; i++) {
//               const actionPatternNode = new PatternTraceNode2(NodeType.ACTION_PATTERN)
//               const group = matchGroups3[i]
//               const groupPlans = tmpPlans.splice(0, group.length)
//               actionPatternNode.init(this, batchNode, tmpNames[0], startIdx2, startIdx2 + groupPlans.length)
//               batchNode.children.push(actionPatternNode)
//
//               for (let j = 0; j < group.length; j++) {
//                 const actionName = tmpNames.shift()
//                 const actionNode = new PatternTraceNode2(NodeType.ACTION)
//                 actionNode.init(this, actionPatternNode, actionName, startIdx2, startIdx2 + 1)
//                 actionPatternNode.children.push(actionNode)
//
//                 startIdx2 += 1
//               }
//             }
//             // assert(startIdx2 === batchNode.endIdx, `batch plan check failed: ${batchNode.name} ${startIdx2} ${batchNode.endIdx}`)
//           }
//         }
//
//       }
//     }
//
//     console.log(this.root)
//   }
//
//   inferBatchName(batchPlans) {
//     const firstName = batchPlans[0].meta.batchName
//     if (firstName === "Planning") return "Prepare Planning"
//     if (firstName != null) return firstName !== 'SoftTrans' ? firstName : "Unknown"
//     if (batchPlans[0].meta.getSimpleName() === 'SpecialLimits') {
//       return "Physical Planning"
//     }
//     for (const plan of batchPlans) {
//       if (plan.meta.getSimpleName() !== 'SoftTrans') {
//         return plan.meta.batchName
//       }
//     }
//     return "Unknown"
//   }
//
//   // /**
//   //  * @param {Pattern} pattern
//   //  * @param {string[]} names
//   //  * @returns {string[][]}
//   //  */
//   // matchPattern(pattern, names) {
//   //   let p = 0, q = 0
//   //   const items = pattern.items
//   //   const matchGroups = items.map(() => [])
//   //   while (p < items.length && q < names.length) {
//   //     const item = items[p]
//   //     let name = names[q]
//   //     switch (item.desc) {
//   //       case "":
//   //         assert(name === item.name)
//   //         matchGroups[p].push(name)
//   //         p++
//   //         q++
//   //         break
//   //       case "+":
//   //         while (name === item.name) {
//   //           matchGroups[p].push(name)
//   //           q++
//   //           if (q >= names.length) break
//   //           name = names[q]
//   //         }
//   //         p++
//   //         break
//   //       case "?":
//   //         if (name === item.name) {
//   //           matchGroups[p].push(name)
//   //           p++
//   //           q++
//   //         } else {
//   //           p++
//   //         }
//   //         break
//   //       case "*":
//   //         while (name === item.name) {
//   //           matchGroups[p].push(name)
//   //           q++
//   //           if (q >= names.length) break
//   //           name = names[q]
//   //         }
//   //         p++
//   //         break
//   //       default:
//   //         assert(false)
//   //     }
//   //   }
//   //   if (matchGroups.reduce((acc, cur) => acc + cur.length, 0) !== names.length){
//   //     console.log(pattern, matchGroups, names)
//   //   }
//   //   assert(matchGroups.reduce((acc, cur) => acc + cur.length, 0) === names.length)
//   //   return matchGroups
//   // }
//
//   /**
//    * @param {string[]} names
//    * @returns {string[][]}
//    */
//   matchPattern(names) {
//     let last = ''
//     let group = []
//     const matchGroups = []
//     for (let i = 0; i < names.length; i++) {
//       const name = names[i]
//       if (last === '') {
//         last = name
//         group.push(name)
//       } else if (last === name) {
//         group.push(name)
//       } else {
//         matchGroups.push(group)
//         group = [name]
//         last = name
//       }
//     }
//     matchGroups.push(group)
//     console.log(matchGroups)
//
//     assert(matchGroups.reduce((acc, cur) => acc + cur.length, 0) === names.length)
//     return matchGroups
//   }
//
//   /**
//    * @param {ConfigV3} config
//    */
//   initialLayout(config) {
//     this.updateNavLayout(config)
//     this.root.initialLayout(config, 0)
//     this.initPlanBlocks(config)
//     this.updateLayout(config)
//     this.initColorMap()
//   }
//
//   updateNavLayout(config) {
//     const {rowHeight, blockExtraHeight, planDagMarginTop} = config.nav
//     this.selectedNodes = this.getSelectedNodes()
//     this.maxLevel = this.selectedNodes.reduce((acc, cur) => Math.max(acc, cur.level), 0)
//     this.planDagStartY = this.maxLevel * rowHeight + blockExtraHeight + planDagMarginTop
//   }
//
//   /**
//    * @param {ConfigV3} config
//    */
//   initPlanBlocks(config) {
//     const {rowHeight, blockWidth, blockExtraHeight} = config.nav
//
//     const vPlanDags = [this.selectedNodes[0].startVPlanDag, ...this.selectedNodes.map(node => node.endVPlanDag)]
//     this.planBlocks = vPlanDags.map((dag, i) => new PlanBlock(this, this.root, i, dag))
//
//     /* compute layout of each block rect */
//
//     const firstBlock = this.planBlocks[0]
//     firstBlock.centerX = 0
//     firstBlock.topY = 0
//     firstBlock.width = blockWidth
//     firstBlock.height = rowHeight * this.maxLevel + blockExtraHeight
//
//     for (let i = 1; i < this.planBlocks.length - 1; i++) {
//       const leftNode = this.selectedNodes[i - 1]
//       const rightNode = this.selectedNodes[i]
//       const planBlock = this.planBlocks[i]
//       planBlock.centerX = rightNode.x
//       planBlock.topY = Math.min(leftNode.y, rightNode.y)
//       planBlock.width = blockWidth
//       const minLevel = Math.min(leftNode.level, rightNode.level)
//       planBlock.height = rowHeight * (this.maxLevel + 1 - minLevel) + blockExtraHeight
//     }
//
//     const lastBlock = this.planBlocks[this.planBlocks.length - 1]
//     lastBlock.centerX = this.root.x + this.root.width
//     lastBlock.topY = 0
//     lastBlock.width = blockWidth
//     lastBlock.height = rowHeight * this.maxLevel + blockExtraHeight
//
//     // initial layout of vPlanDag
//     for (const planBlock of this.planBlocks) {
//       const dag = planBlock.vPlanDag
//       dag.y = this.planDagStartY
//       dag.x = planBlock.centerX - dag.width / 2
//     }
//
//     // compute change label
//     vPlanDags.forEach(dag => dag.nodes.forEach(node => node.evoLabels = []))
//     for (let i = 0; i < vPlanDags.length - 1; i++) {
//       const dag0 = vPlanDags[i], dag1 = vPlanDags[i + 1]
//       const vidList0 = dag0.nodes.map(node => node.vid)
//       const vidList1 = dag1.nodes.map(node => node.vid)
//
//       const added = _.difference(vidList1, vidList0)
//       for (const vid of added) {
//         dag1.nodeMap.get(vid).evoLabels.push('added')
//       }
//
//       const toRemove = _.difference(vidList0, vidList1)
//       for (const vid of toRemove) {
//         dag0.nodeMap.get(vid).evoLabels.push('to_remove')
//       }
//     }
//   }
//
//   initColorMap() {
//     let idx = 0
//     const collectColor = (node) => {
//       const name = node.getSimpleName()
//       if (!this.colorMap.has(name)) {
//         this.colorMap.set(name, idx++)
//       }
//       for (const child of node.children) {
//         collectColor(child)
//       }
//     }
//
//     collectColor(this.root)
//   }
//
//   getColor(node) {
//     const name = node.getSimpleName()
//     const idx = this.colorMap.get(name)
//     return this.color(idx % 10)
//   }
//
//   /**
//    * @param {ConfigV3} config
//    */
//   // eslint-disable-next-line no-unused-vars
//   updateLayout(config) {
//     const {margin} = config.plan
//
//     this.width = this.root.width
//         + this.planBlocks[0].vPlanDag.width / 2
//         + this.planBlocks[this.planBlocks.length - 1].vPlanDag.width / 2
//         + margin * 2
//     this.height = this.planBlocks.reduce((acc, cur) => Math.max(acc, cur.vPlanDag.y + cur.vPlanDag.height), 0)
//         + margin
//     this.startX = margin + this.planBlocks[0].vPlanDag.width / 2
//     this.startY = 0
//   }
//
//   getSelectedNodes() {
//     const nodes = []
//     const collect = (node) => {
//       if (!node.expanded) {
//         nodes.push(node)
//       } else {
//         for (const child of node.children) {
//           collect(child)
//         }
//       }
//     }
//     collect(this.root)
//     return nodes
//   }
//
//   getVPlanDag(idx) {
//     assert(idx >= 0 && idx < this.vPlanDags.length, 'Invalid idx ' + idx)
//     let dag = this.vPlanDags[idx]
//     if (dag === null) {
//       dag = new VPlanDag()
//       dag.init(this.plans[idx])
//       this.vPlanDags[idx] = dag
//     }
//     return dag
//   }
//
//   toggleTraceNode(config, node) {
//     node.expanded = !node.expanded
//     // temp
//     this.updateNavLayout(config)
//     this.root.initialLayout(config, 0)
//     this.initPlanBlocks(config)
//     this.updateLayout(config)
//   }
// }
//
// export class PatternTraceNode2 {
//   /** @type {PatternTraceTree2} */
//   traceTree
//   /** @type {PatternTraceNode2} */
//   parent = null
//   /** @type {PatternTraceNode2[]} */
//   children = []
//   /** @type {NodeType} */
//   nodeType
//   /** @type {string} */
//   name = 'Unknown'
//   // the plan slice [startIdx, endIdx)
//   /** @type {number} */
//   startIdx = 0
//   /** @type {number} */
//   endIdx = 0
//   /** @type {number} */
//   level
//
//   desc
//
//   // layout of corresponding rectangle
//   x = 0
//   y = 0
//   width = 0
//   height = 0
//
//   color = '#000000'
//
//   hints = []
//
//   // interaction
//   expanded = false
//
//   constructor(nodeType) {
//     this.nodeType = nodeType
//   }
//
//   /**
//    * @param {PatternTraceTree2} traceTree
//    * @param {PatternTraceNode2} parent
//    * @param {string} name
//    * @param {number} startIdx
//    * @param {number} endIdx
//    * @param {?string} desc
//    */
//   init(traceTree, parent, name, startIdx, endIdx, desc=null) {
//     this.traceTree = traceTree
//     this.parent = parent
//     this.name = name
//     this.startIdx = startIdx
//     this.endIdx = endIdx
//     this.level = parent ? parent.level + 1 : 0
//     this.desc = desc
//   }
//
//   setExpanded(expanded) {
//     this.expanded = expanded
//   }
//
//   isPatternNode() {
//     return this.nodeType.includes('pattern')
//   }
//
//   /**
//    * @returns {VPlanDag}
//    */
//   get startVPlanDag() {
//     return this.traceTree.getVPlanDag(this.startIdx)
//   }
//
//   /**
//    * @returns {VPlanDag}
//    */
//   get endVPlanDag() {
//     return this.traceTree.getVPlanDag(this.endIdx)
//   }
//
//   getPlans() {
//     return this.traceTree.plans.slice(this.startIdx, this.endIdx + 1)
//   }
//
//   get planRatio() {
//     if (this.isRoot) return 0
//     return this.getPlans().length / this.parent.getPlans().length
//   }
//
//   getTimeCost() {
//     return this.getPlans().reduce((acc, cur) => acc + cur.meta.runTime ?? 0, 0)
//   }
//
//   getSimpleName() {
//     let name = this.name
//     if (!name || name === '') {
//       name = 'Unknown'
//     }
//     if (name.endsWith("$")) {
//       name = name.substring(0, name.length - 1)
//     }
//     if (name.includes('.')) {
//       name = name.split('.')[1]
//     }
//     if (name.includes("$")) {
//       name = name.split("$")[1]
//     }
//     return name
//   }
//
//   getSimpleNameWithCnt() {
//     let name = this.getSimpleName()
//     if (this.isPatternNode() && this.children.length > 1) {
//       name += ` (${this.children.length})`
//     }
//     return name
//   }
//
//   get isRoot() {
//     return this.nodeType === NodeType.ROOT
//   }
//
//   toString() {
//     return this.name
//   }
//
//   /**
//    * Compute the layout of rect, call it recursively
//    * @param {ConfigV3} config
//    * @param {number} x
//    */
//   initialLayout(config, x) {
//     const {rowHeight} = config.nav
//     const {margin} = config.plan
//
//     this.x = x
//     this.y = (this.level - 1) * rowHeight   // first level (root) will be ignored
//     this.height = rowHeight
//     this.width = 0
//
//     if (this.expanded) {
//       let startX = x
//       for (let i = 0; i < this.children.length; i++) {
//         const child = this.children[i]
//         child.initialLayout(config, startX)
//         startX += child.width
//       }
//       this.width = startX - x
//     } else {
//       const startDag = this.startVPlanDag
//       const endDag = this.endVPlanDag
//       startDag.layoutOnce(config)
//       endDag.layoutOnce(config)
//       // if (this.getSimpleName() === 'Replace Operators' || this.getSimpleName() === 'ReplaceDeduplicateWithAggregate') {
//       //   console.log(startDag.width, endDag.width, startDag, endDag, startDag.plan.pid, endDag.plan.pid)
//       // }
//       this.width = (startDag.width + endDag.width) / 2 + margin * 2
//     }
//   }
// }
//
// export class PlanBlock {
//   /** @type {PatternTraceTree2} */
//   traceTree
//   /** @type {PatternTraceNode2} */
//   parentNode
//   /** @type {number} */
//   idx
//   /** @type {VPlanDag} */
//   vPlanDag
//
//   centerX = 0
//   topY = 0
//   width = 0
//   height = 0
//
//   /**
//    * @param {PatternTraceTree2} traceTree
//    * @param {PatternTraceNode2} parentNode
//    * @param {number} idx the position this plan located. 0 means the first plan in the front of the trace node (action)
//    * @param {VPlanDag} vPlanDag
//    */
//   constructor(traceTree, parentNode, idx, vPlanDag) {
//     this.traceTree = traceTree
//     this.parentNode = parentNode
//     this.vPlanDag = vPlanDag
//     this.idx = idx
//   }
//
//   get level() {
//     return this.parentNode.level + 1
//   }
// }
//
