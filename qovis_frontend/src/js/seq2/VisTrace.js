//
// export class VisTrace {
//   /** @type {TraceTree} */
//   traceTree
//   /** @type {(ActionBlock | PlanBlock)[][]} */
//   rows
//   /** @type {PlanBlock[]} */
//   planBlocks
//
//   /**
//    * @param {ConfigV3} config
//    * @param {TraceTree} traceTree
//    */
//   init(config, traceTree) {
//     this.traceTree = traceTree
//     this.rows = []
//     this.planBlocks = []
//
//     // at the beginning, there are only two rows (root is expanded)
//     this.rows.push([this.traceTree.root])
//     this.rows.push([])
//   }
// }
//
// export class Block {
//   /** @type {VisTrace} */
//   visTrace
//   /** @type {'action' | 'plan'} */
//   type
//   /** @type {number} */
//   rowIdx
//   /** @type {number} */
//   idx
//
//   constructor(visTrace, rowIdx, idx) {
//     this.visTrace = visTrace
//     this.rowIdx = rowIdx
//     this.idx = idx
//   }
//
//   // layout
//   x = 0
//   y = 0
//   width = 0
//   height = 0
// }
//
// export class ActionBlock extends Block {
//   type = 'action'
//   /** @type {Meta} */
//   meta
//   /** @type {traceNode} */
//   traceNode
//
//   constructor(visTrace, rowIdx, idx, meta, traceNode) {
//     super(visTrace, rowIdx, idx)
//     this.meta = meta
//     this.traceNode = traceNode
//   }
// }
//
// export class PlanBlock extends Block {
//   type = 'plan'
//   /** @type {Plan} */
//   plan
//   /** @type {VisPlan} */
//   visPlan
//
//   constructor(visTrace, rowIdx, idx, plan, visPlan) {
//     super(visTrace, rowIdx, idx)
//     this.plan = plan
//     this.visPlan = visPlan
//   }
// }
