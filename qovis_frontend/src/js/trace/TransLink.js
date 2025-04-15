import {VisTransLink} from "@/js/trace/VisTransLink"

/**
 * @enum {string}
 * @readonly
 */
export const LinkKind = {
  EQ: 'eq',
  CH: 'ch',
  PEQ: 'peq',
}

export class TransLink {
  /** @type {import('@/js/trace/PlanNode').PlanNode} */
  node0
  /** @type {import('@/js/trace/PlanNode').PlanNode} */
  node1
  /** @type {LinkKind} */
  kind
  /** @type {string | null} */
  param0
  /** @type {string | null} */
  param1
  /** @type {int | null} */
  paramIdx0
  /** @type {int | null} */
  paramIdx1
  /** @type {string[]} */
  rules

  /** @type {ParamItem} */
  srcParamItem = null
  /** @type {ParamItem} */
  dstParamItem = null

  /** @type {VisTransLink} */
  visObj = null

  /**
   * @param {PlanNode} node0
   * @param {PlanNode} node1
   * @param {LinkKind} kind
   * @param {string | null} param0
   * @param {string | null} param1
   * @param {int | null} paramIdx0
   * @param {int | null} paramIdx1
   * @param {string[]} rules
   */
  constructor(node0, node1, kind,
              param0, param1, paramIdx0, paramIdx1,
              rules) {
    this.node0 = node0
    this.node1 = node1
    this.kind = kind
    this.param0 = param0
    this.param1 = param1
    this.paramIdx0 = paramIdx0
    this.paramIdx1 = paramIdx1
    this.rules = rules

    this.srcParamItem = this.node0.paramItemsMap.get(param0)[paramIdx0 ?? 0]
    this.dstParamItem = this.node1.paramItemsMap.get(param1)[paramIdx1 ?? 0]
  }

  /**
   * @returns {VisTransLink}
   */
  createVisObj() {
    this.visObj = new VisTransLink(this)
    return this.visObj
  }

  toString() {
    // python code
    //     def __str__(self):
    //         def node_str(node: PlanNode):
    //             return f'{node.name}#{node.vid}'
    //
    //         def param_str(node, param, param_idx):
    //             return f'{node_str(node)}.{param}[{param_idx}]'
    //
    //         if self.kind == self.LinkKind.EQ:
    //             return f'EqLink({param_str(self.node0, self.param0, self.param_idx0)} == ' \
    //                    f'{param_str(self.node1, self.param1, self.param_idx1)})'
    //         elif self.kind == self.LinkKind.CH:
    //             return f'ChLink({param_str(self.node0, self.param0, self.param_idx0)} -> ' \
    //                    f'{param_str(self.node1, self.param1, self.param_idx1)})'
    //         elif self.kind == self.LinkKind.PEQ:
    //             return f'PEqLink({param_str(self.node0, self.param0, self.param_idx0)} == ' \
    //                    f'{param_str(self.node1, self.param1, self.param_idx1)})'
    //         else:
    //             raise Exception(f'Unknown link kind {self.kind}')

    const nodeStr = (node) => `Plan#${node.plan.pid}.${node.name}#${node.vid}`
    const paramStr = (node, param, paramIdx) => `${nodeStr(node)}.${param}[${paramIdx}]`

    if (this.kind === LinkKind.EQ) {
      return `EqLink(${paramStr(this.node0, this.param0, this.paramIdx0)} == ` +
          `${paramStr(this.node1, this.param1, this.paramIdx1)})`
    }
    if (this.kind === LinkKind.CH) {
      return `ChLink(${paramStr(this.node0, this.param0, this.paramIdx0)} -> ` +
          `${paramStr(this.node1, this.param1, this.paramIdx1)})`
    }
    if (this.kind === LinkKind.PEQ) {
      return `PEqLink(${paramStr(this.node0, this.param0, this.paramIdx0)} == ` +
          `${paramStr(this.node1, this.param1, this.paramIdx1)})`
    }
    throw new Error(`Unknown link kind ${this.kind}`)
  }

  // /**
  //  * @param {TransLink} other
  //  * @return {TransLink}
  //  */
  // merge(other) {
  //   // python code
  //   //         assert self.node1.vid == other.node0.vid
  //   //         assert self.kind != self.LinkKind.PEQ and other.kind != self.LinkKind.PEQ
  //   //         if self.kind == self.LinkKind.EQ and other.kind == self.LinkKind.EQ:
  //   //             return TransLink.mk_eq(self.node0, other.node1,
  //   //                                    self.param0, other.param1,
  //   //                                    self.param_idx0, other.param_idx1)
  //   //         elif other.kind == self.LinkKind.EQ:
  //   //             return TransLink.mk_ch(self.node0, other.node1,
  //   //                                    self.param0, self.param1,
  //   //                                    self.param_idx0, self.param_idx1)
  //   //         elif self.kind == self.LinkKind.EQ:
  //   //             return TransLink.mk_ch(self.node0, other.node1,
  //   //                                    other.param0, other.param1,
  //   //                                    other.param_idx0, other.param_idx1)
  //   //         else:
  //   //             return TransLink.mk_ch(self.node0, other.node1,
  //   //                                    self.param0, other.param1,
  //   //                                    self.param_idx0, other.param_idx1)
  //   if (this.node1.vid !== other.node0.vid) {
  //     throw new Error('cannot merge two links')
  //   }
  //   if (this.kind === LinkKind.PEQ || other.kind === LinkKind.PEQ) {
  //     throw new Error('cannot merge two links')
  //   }
  //   if (this.kind === LinkKind.EQ && other.kind === LinkKind.EQ) {
  //     return new TransLink(
  //         this.node0, other.node1,
  //         LinkKind.EQ,
  //         this.param0, other.param1,
  //         this.paramIdx0, other.paramIdx1)
  //   } else if (other.kind === LinkKind.EQ) {
  //     return new TransLink(
  //         this.node0, other.node1,
  //         LinkKind.CH,
  //         this.param0, this.param1,
  //         this.paramIdx0, this.paramIdx1)
  //   } else if (this.kind === LinkKind.EQ) {
  //     return new TransLink(
  //         this.node0, other.node1,
  //         LinkKind.CH,
  //         other.param0, other.param1,
  //         other.paramIdx0, other.paramIdx1)
  //   } else {
  //     return new TransLink(
  //         this.node0, other.node1,
  //         LinkKind.CH,
  //         this.param0, other.param1,
  //         this.paramIdx0, other.paramIdx1)
  //   }
  // }
}
