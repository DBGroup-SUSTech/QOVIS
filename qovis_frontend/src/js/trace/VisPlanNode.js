import {Node} from "@/js/common/Graph"

/**
 * @extends {import('@/js/common/Graph').Node<VisPlanNode, VisPlanEdge>}
 */
export class VisPlanNode extends Node {
  /** @type {import('@/js/trace/PlanNode').PlanNode} */
  origin = null
  /** @type {Map<string, VisParamItem[]>} */
  paramMap = new Map()
  /** @type {[string, VisParamItem[][]]} */
  paramData = []

  /** @type {int} */
  level   // set by VisPlan

  width
  height
  x
  y

  levelTopY
  levelBottomY

  /** @type {['added' | 'to_remove']} */
  evoLabels = []

  constructor() {
    super()
  }

  assignOrigin(origin) {
    this.origin = origin
    this.computeParamRowData()
    return this
  }

  /**
   * @param {VisQueryPlan} plan
   */
  initItemLinks(plan) {
    for (const items of this.paramMap.values()) {
      for (const item of items) {
        item.initLinks(plan)
      }
    }
  }

  get children() {
    return this.inEdges.map(e => e.src)
  }

  toString() {
    return this.origin?.toString() ?? ""
  }

  toLimitedString(charLimit) {
    let str = this.toString()
    if (str.length > charLimit) {
      return str.slice(0, charLimit - 3) + '...'
    } else {
      return str
    }
  }

  getNodeName() {
    return this.origin.name
  }

  getNodeId() {
    return this.origin.vid
  }

  isAdded() {
    return this.evoLabels.includes('added')
  }

  toRemove() {
    return this.evoLabels.includes('to_remove')
  }

  get planNodeStr() {
    return this.origin.str.split('\n')[1]
  }

  layout(config) {
    // eslint-disable-next-line no-unused-vars
    const {nodeWidth, nodeTitleHeight, paramRowHeight} = config.plan
    this.layoutParamItems(config)

    // this.width = useOptAlias ? nodeWidthAlias : nodeWidth
    this.width = nodeWidth
    const paramHeight = this.paramData.reduce((acc, val) => {
      return acc + val[1].length * paramRowHeight
    }, 0)
    this.height = nodeTitleHeight + paramHeight
  }

  computeParamRowData() {
    this.paramData = []
    this.paramMap.clear()

    for (const kind of this.origin.paramKinds) {
      this.paramData.push([kind, []])   // compute when layout
    }

    for (const [kind, items] of this.origin.paramItemsMap.entries()) {
      this.paramMap.set(kind, items.map(item => item.createVisObj()))
    }
  }

  layoutParamItems(config) {
    const {paramFontSize, nodeWidth, paramItemMaxWidth, paramRowHeight,
      paramItemPadding, paramItemMargin, paramItemBaseColor, paramRowLeftRight} = config.plan

    let rowCnt = 0
    for (const [kind, rows] of this.paramData) {
      const items = this.paramMap.get(kind)
      // remove all elements in rows
      rows.splice(0, rows.length)

      // compute rows
      if (items.length === 1) {
        const item = items[0]
        item.layout(nodeWidth - 2 * paramItemMargin, paramItemPadding, paramFontSize)
        item.y = rowCnt * paramRowHeight
        item.color = paramItemBaseColor
        rows.push(items)    // only 1 item, so only 1 row
        rowCnt += 1
      } else {
        items.forEach(item => item.layout(paramItemMaxWidth, paramItemPadding, paramFontSize))
        // divided into rows
        /** @type {VisParamItem[][]} */
        let curX = paramRowLeftRight
        let curRow = []
        for (let i = 0; i < items.length; i++) {
          const item = items[i]
          if (curX + item.width > nodeWidth - paramRowLeftRight) {
            rows.push(curRow)
            curRow = []
            rowCnt += 1
            curX = paramRowLeftRight
          }
          item.x = curX
          item.y = rowCnt * paramRowHeight
          item.color = paramItemBaseColor
          curRow.push(item)
          curX += item.width + paramItemMargin
        }
        if (curRow.length > 0) {
          rows.push(curRow)
          rowCnt += 1
        }
      }

      // center rows
      rows.forEach(row => {
        const rowSpan = row.reduce((acc, item) => {
          return acc + item.width
        }, 0) + (row.length - 1) * paramItemMargin
        let curX = (nodeWidth - rowSpan) / 2
        row.forEach(item => {
          item.x = curX
          curX += item.width + paramItemMargin
        })
      })
    }
  }
}
