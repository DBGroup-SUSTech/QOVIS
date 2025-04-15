import {OverviewDag} from "@/js/overview-dag/OverviewDag"
import {TraceNode} from "@/js/trace-dag/TraceNode"
import {TraceEdge} from "@/js/trace-dag/TraceEdge"
import {NestedDag} from "@/js/nested-dag/NestedDag"

export class TraceDag {
  /** @type {TraceNode[]} */
  nodes = []
  /** @type {Map<int, TraceNode>} */
  nodeMap = new Map()
  /** @type {TraceEdge[]} */
  edges = []
  /** @type {Map<String, TraceEdge>} */
  edgeMap = new Map()

  /** @type {OverviewDag} */
  overviewObj
  /** @type {NestedDag} */
  nestedObj

  constructor(rawTraceDag) {
    this.build(rawTraceDag)
    this.computeRank()
    // this.computeRankGroup()
  }

  build(rawTraceDag) {
    const rawNodes = rawTraceDag.nodes
    const rawEdges = rawTraceDag.edges

    for (const rawNode of rawNodes) {
      const node = new TraceNode(this)
      Object.assign(node, rawNode)
      Object.freeze(node.meta)
      this.nodes.push(node)
      this.nodeMap.set(node.nid, node)
    }
    for (const rawEdge of rawEdges) {
      const edge = new TraceEdge(this)
      Object.assign(edge, rawEdge)
      Object.freeze(edge.meta)
      this.edges.push(edge)
      this.edgeMap.set(edge.eid, edge)
    }

    // for (const node of this.nodes) {
    //   node.inEdges = node.inEdges.map(eid => this.edgeMap.get(eid))
    //   node.outEdges = node.outEdges.map(eid => this.edgeMap.get(eid))
    // }
    // for (const edge of this.edges) {
    //   edge.src = this.nodeMap.get(edge.src)
    //   edge.dst = this.nodeMap.get(edge.dst)
    // }
  }

  computeRank() {
    if (this.nodes.length === 0) {
      return
    }

    let startNode = this.nodes[0]
    while (startNode.inEdges.length !== 0) {
      startNode = startNode.getInEdge(0).src
    }

    let rank = 0
    let curLevel = [startNode]
    while (curLevel.length !== 0) {
      curLevel.forEach(node => node.rank = rank)
      curLevel = curLevel.flatMap(node => node.getOutEdges())
          .map(e => e.getDst())
      rank += 1
    }
    this.nodes.sort((a, b) => a.rank - b.rank)
  }

  createOverviewObj() {
    const obj = new OverviewDag(this)
    this.overviewObj = obj
    return obj
  }

  createNestedObj() {
    const obj = new NestedDag(this)
    this.nestedObj = obj
    return obj
  }

  computeRankGroup() {
    const groupMap = new Map()
    for (const node of this.nodes) {
      if (groupMap.has(node.rank)) {
        groupMap.get(node.rank).push(node)
      } else {
        groupMap.set(node.rank, [node])
      }
    }
    const items = Array.from(groupMap.entries())
    items.sort((p, q) => p[0] - q[0])
    this.rankGroups = items.map(it => it[1])
    // .filter(it => it.some(node => node.nodeType !== 'plan'))

    this.rankGroups = Object.freeze(this.rankGroups)
  }

  temp(rawTraceDag) {
    const rawNodes = rawTraceDag.nodes
    const rawEdges = rawTraceDag.edges
    const rawNodeMap = new Map()
    const rawEdgeMap = new Map()

    rawNodes.forEach(rn => {
      rn = Object.assign({}, rn)
      rawNodeMap.set(rn.nid, rn)
    })
    rawEdges.forEach(re => {
      re = Object.assign({}, re)
      rawEdgeMap.set(re.eid, re)
    })
    rawNodes.forEach(rn => {
      rn.inEdges = rn.inEdges.map(eid => rawEdgeMap.get(eid))
      rn.outEdges = rn.outEdges.map(eid => rawEdgeMap.get(eid))
    })
    rawEdges.forEach(re => {
      re.src = rawNodeMap.get(re.src)
      re.dst = rawNodeMap.get(re.dst)
    })

    rawNodes.filter(rn => rn.nodeType === 'plan')
        .forEach(rn => {
          const node = Object.assign({}, rn, {
            inEdges: [],
            outEdges: [],
          })
          this.nodes.push(node)
          this.nodeMap.set(node.nid, node)
        })
    rawNodes.filter(rn => rn.nodeType !== 'plan')
        .forEach(rn => {
          const edgeMeta = Object.assign({}, rn, {
            nid: undefined,
            inEdges: undefined,
            outEdges: undefined,
          })
          rn.inEdges.forEach(inEdge => {
            rn.outEdges.forEach(outEdge => {
              const src = this.nodeMap.get(inEdge.src.nid)
              const dst = this.nodeMap.get(outEdge.dst.nid)
              const edge = {
                eid: `${src.nid}-${dst.nid}`,
                src, dst,
                ...edgeMeta,
              }
              src.outEdges.push(edge)
              dst.inEdges.push(edge)
              this.edges.push(edge)
              this.edgeMap.set(edge.eid, edge)
            })
          })
        })

  }
}
