export class NestedDag {
  /** @type {TraceDag} */
  traceDag

  /** @type {NestedNode[]} */
  nodes = []
  /** @type {NestedEdge[]} */
  edges = []

  width = 0
  height = 0

  rankGroups

  constructor(traceDag) {
    this.traceDag = traceDag
    this.init()
  }

  init() {
    this.nodes = this.traceDag.nodes.map(v => v.createNestedObj(this))
    this.edges = this.traceDag.edges.map(e => e.createNestedObj(this))
  }

  computeRankGroups() {
    const groupMap = new Map()
    for (const node of this.nodes) {
      if (groupMap.has(node.traceNode.rank)) {
        groupMap.get(node.traceNode.rank).push(node)
      } else {
        groupMap.set(node.traceNode.rank, [node])
      }
    }
    const items = Array.from(groupMap.entries())
    items.sort((p, q) => p[0] - q[0])
    this.rankGroups = items.map(it => it[1])
  }
}
