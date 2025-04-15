import {VisParamItem} from "@/js/trace/VisParamItem"

export class ParamItem {
  /** @type {import('@/js/trace/PlanNode').PlanNode} */
  node
  /** @type {string} */
  paramKind
  /** @type {int | null} */
  paramIdx
  /** @type {string} */
  content

  /** @type {TransLink[]} */
  prevLinks = []
  /** @type {TransLink[]} */
  nextLinks = []
  isEqPrev = false
  isEqNext = false

  /** @type {VisParamItem} */
  visObj = null

  constructor(node, paramKind, paramIdx, content) {
    this.node = node
    this.paramKind = paramKind
    this.paramIdx = paramIdx
    this.content = content
  }

  createVisObj() {
    this.visObj = new VisParamItem(this)
    return this.visObj
  }

  toString() {
    const nodeStr = (node) => `Plan#${node.plan.pid}.${node.name}#${node.vid}`
    const paramStr = (node, param, paramIdx) => `${nodeStr(node)}.${param}[${paramIdx}]`
    return `${paramStr(this.node, this.paramKind, this.paramIdx)}: ${this.content}`
  }
}
