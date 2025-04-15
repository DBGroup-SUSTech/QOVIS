// import assert from "assert"
// import _ from "lodash"
//
// export class OptTrace {
//   /** @type {Rule[]} */
//   rules = []
//   /** @type {Plan[]} */
//   plans = []
//
//   /**
//    * @param {ConfigV2} config
//    * @param {DynamicGraph} dg
//    * @param {Pattern[]} patterns
//    */
//   init(config, dg, patterns) {
//     this.plans = dg.plans
//     this.rules = dg.plans.slice(1)
//         .map(p => {
//           const rule = new Rule()
//           rule.name = p.meta.getSimpleName()
//           rule.labels = []
//           rule.meta = p.meta
//           return rule
//         })
//
//     /* add labels to rules */
//     const name2rankId = new Map()
//
//     const phaseNames = dg.phaseNames
//     const phaseIntervals = dg.phaseIntervals
//     assert(phaseNames.length === phaseIntervals.length)
//
//     for (const [phaseName, [start, end]] of _.zip(phaseNames, phaseIntervals)) {
//       let name, rankId
//       if (phaseName.includes('#')) {
//         name = phaseName.split('#')[0]
//       } else {
//         name = phaseName
//       }
//
//       if (name2rankId.has(name)) {
//         rankId = name2rankId.get(name)
//         name2rankId.set(name, rankId + 1)
//       } else {
//         rankId = 0
//         name2rankId.set(name, 1)
//       }
//
//       // add batch label / id to rules as the first label / id
//       for (let i = start; i < end - 1; i++) {   // we have slice(1) when processing rules
//         const rule = this.rules[i]
//         rule.labels.push(name)
//         rule.rankIdList.push(rankId)
//       }
//     }
//
//     const tmpPhaseNames = phaseNames.slice()
//     for (const [start, end] of phaseIntervals) {
//       const plan = this.plans.slice(start + 1, end)
//     }
//   }
// }
//
// export class Rule {
//   /** @type {string} */
//   name
//   /** @type {string[]} */
//   labels = []
//   /** @type {number[]} */
//   rankIdList = []
//   /** @type {Meta} */
//   meta
//
//   toString() {
//     return `${this.name}#${this.rankIdList[this.rankIdList.length - 1]}`
//   }
// }
