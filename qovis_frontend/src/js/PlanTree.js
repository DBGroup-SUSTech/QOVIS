// export class PlanTree {
//   nodes = []
//   nodeMap = new Map()
//   root = null
//
//   constructor(plan) {
//     this.build(plan)
//   }
//
//   build(plan) {
//     this.nodes = plan
//     this.nodes.forEach(node => {
//       this.nodeMap.set(node.id, node)
//       node.children = []
//     })
//     this.root = this.nodes[0]
//     const nodeStack = [this.root]
//     const childCntStack = [this.root['childCnt']]
//     for (let i = 1; i < this.nodes.length; i++) {
//       const node = this.nodes[i]
//       while (lastItem(childCntStack) === 0) {
//         nodeStack.splice(nodeStack.length - 1, 1)
//         childCntStack.splice(childCntStack.length - 1, 1)
//       }
//       // find the parent
//       lastItem(nodeStack).children.push(node)
//       childCntStack[childCntStack.length - 1] -= 1
//       // add cur node
//       nodeStack.push(node)
//       childCntStack.push(node['childCnt'])
//     }
//   }
// }
