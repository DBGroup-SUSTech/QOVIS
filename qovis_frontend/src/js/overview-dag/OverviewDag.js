export class OverviewDag {
  /** @type {TraceDag} */
  traceDag

  /** @type {OverviewNode[]} */
  nodes = []
  /** @type {OverviewEdge[]} */
  edges = []

  width = 0
  height = 0

  constructor(traceDag) {
    this.traceDag = traceDag
    this.init()
  }

  init() {
    this.nodes = this.traceDag.nodes.map(v => v.createOverviewObj(this))
    this.edges = this.traceDag.edges.map(e => e.createOverviewObj(this))
  }

  computeLayout({paddingX, paddingY, gapX, gapY}) {
    const groupMap = new Map()
    for (const node of this.nodes) {
      const rank = node.traceNode.rank
      if (groupMap.has(rank)) {
        groupMap.get(rank).push(node)
      } else {
        groupMap.set(rank, [node])
      }
    }
    this.nodes.forEach(node => {
      const rank = node.traceNode.rank
      node.x = paddingX + gapX * groupMap.get(rank).indexOf(node)
      node.y = paddingY + gapY * rank
    })

    this.nodes.forEach(node => {
      const {x, y} = node
      this.width = Math.max(x + paddingX, this.width)
      this.height = Math.max(y + paddingY, this.height)
    })
  }
}
