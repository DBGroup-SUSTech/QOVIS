// have been segmented by intervals
import {VisNode} from "@/js/main-view/VisNode"
import {VisPlan} from "@/js/main-view/VisPlan"
import dagre from "dagre"
import * as d3 from 'd3'
import {VisTran} from "@/js/main-view/VisTran"

export class VisGraph {
  /** @type {SGraph[]} */
  sGraphs
  /** @type {Object<int, boolean>[]} */
  effList
  /** @type {Object<int, boolean>[]} */
  keyList

  /** @type {VisNode[]} */
  nodes
  /** @type {Map<int, VisNode>} */
  nodeMap

  /** @type {boolean} */
  show = false

  g

  constructor(sGraph, effList, keyList) {
    this.sGraphs = sGraph
    this.effList = effList
    this.keyList = keyList
    this.init()
  }

  init() {
    this.nodes = []
    this.nodeMap = new Map()

    // hardcode: use max
    let tmpSGraph = this.sGraphs[0]
    let tmpSGraphSize = this.sGraphs[0].nodeMap.size
    this.sGraphs.forEach(sg => {
      if (sg.nodeMap.size > tmpSGraphSize) {
        tmpSGraph = sg
        tmpSGraphSize = sg.nodeMap.size
      }
    })
    for (const node of tmpSGraph.nodeMap.values()) {
      const visNode = new VisNode()
      visNode.vid = node.vid
      visNode.visGraph = this
      this.nodes.push(visNode)
      this.nodeMap.set(visNode.vid, visNode)
    }
    this.nodes.sort((u, v) => u.vid - v.vid)

    for (const edge of tmpSGraph.edgeMap.values()) {
      const src = this.nodeMap.get(edge.src.vid)
      const dst = this.nodeMap.get(edge.dst.vid)
      src.outNodes.push(dst)
      dst.inNodes.push(src)
    }
    this.nodes.forEach(node => {
      node.inNodes.sort((u, v) => u.vid - v.vid)
      node.outNodes.sort((u, v) => u.vid - v.vid)
    })

    for (let i = 0; i < this.sGraphs.length; i++) {
      const sGraph = this.sGraphs[i]
      const effDict = this.effList[i]
      for (const sNode of sGraph.nodeMap.values()) {
        const vid = sNode.vid
        const isEff = effDict[vid]
        if (!isEff) {
          continue
        }
        const visNode = this.nodeMap.get(vid)
        // console.log(this, this.nodeMap, vid)
        // if (visNode.visPlans.length > 0) {
        //   const lastOne = visNode.visPlans[visNode.visPlans.length - 1]
        //   if (lastOne.plan.pid === 9 && sGraph.plan.pid === 13) {
        //     continue
        //   }
        // }
        const visPlan = (new VisPlan()).init(sGraph.plan, sNode.planNodes.map(v => v.vid))
        visNode.visPlans.push(visPlan)
        if (visNode.visPlans.length > 1) {
          // not the first one
          const visTran = (new VisTran()).init(sGraph.plan)
          visNode.visTrans.push(visTran)
        }
      }
    }

    for (const node of this.nodes) {
      if (node.visPlans.length > 1 && node.visPlans[1].plan.meta.type === 'soft trans') {
        node.visPlans.shift()
        node.visTrans.shift()
      }
    }
  }

  layout(conf) {
    for (const node of this.nodes) {
      node.layout(conf)
    }
    // this.nodes.forEach(node => node.layout())

    let g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir:'BT',
      ranksep: '20',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.nodes.forEach(node => {
      g.setNode(node.vid, node)
    })

    this.nodes.forEach(node => {
      node.inNodes.forEach(child => {
        g.setEdge({v: child.vid, w: node.vid})
      })
    })

    dagre.layout(g)

    this.g = g

    // compute total size
    this.width = Math.max(...this.nodes.map(node => {
      return node.x + node.width / 2
    }))
    this.height = Math.max(...this.nodes.map(node => {
      return node.y + node.height / 2
    }))
  }

  getEdges() {
    const ret = []
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.nodes.forEach(node => {
      node.inNodes.forEach(child => {
        const points = this.g.edge({v: child.vid, w: node.vid}).points
        const path = lineGen(points)
        ret.push({
          src: child,
          dst: node,
          points: points,
          path: path,
        })
      })
    })
    return ret
  }
}
