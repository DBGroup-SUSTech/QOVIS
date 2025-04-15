import {ParamItem} from "@/js/trace/ParamItem"

export class PlanNode {
  name
  clazz
  vid
  str
  addr
  /** @type {[string, string | []][]} */
  params    // type might be: pred, attrs, rel, other
  /** @type {QueryPlan} */
  plan

  /** @type {string[]} */
  paramKinds = []
  /** @type {Map<string, ParamItem[]>} */
  paramItemsMap = new Map()

  /** @type {PlanNode | null} */
  parent = null
  /** @type {PlanNode[]} */
  children = []

  /** @type {import('@/js/trace/VisPlanNode.js').VisPlanNode} */
  visObj = null

  /**
   * @param {string} name
   * @param {string} clazz
   * @param {int} vid
   * @param {string} str
   * @param addr
   * @param {[string, string | []][]} params
   * @param {QueryPlan} plan
   */
  constructor(name, clazz, vid, str, addr, params, plan) {
    this.name = name
    this.clazz = clazz
    this.vid = vid
    this.str = str
    this.addr = addr
    this.params = params
    this.plan = plan
    this.initParamItems()
  }

  toString() {
    return `${this.name}#${this.vid} ${this.str}`
  }

  get paramArray() {
    const result = []
    for (const param of this.params) {
      const v = param[1]
      if (Array.isArray(v)) {
        result.push(...v)
      } else {
        result.push(v)
      }
    }
    return result
  }

  initParamItems() {
    // eslint-disable-next-line no-unused-vars
    this.paramKinds = this.params.map(([paramKind, _]) => paramKind)
    this.paramItemsMap.clear()
    for (const [paramKind, paramValue] of this.params) {
      const items = []
      if (Array.isArray(paramValue)) {
        for (const [paramIdx, content] of paramValue.entries()) {
          const item = new ParamItem(this, paramKind, paramIdx, content)
          items.push(item)
        }
      } else {
        const item = new ParamItem(this, paramKind, null, paramValue)
        items.push(item)
      }
      this.paramItemsMap.set(paramKind, items)
    }
  }
}

