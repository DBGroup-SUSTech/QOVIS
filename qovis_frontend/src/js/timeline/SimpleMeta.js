import {TimelineRow} from "@/js/timeline/TimelineRow"
import _ from "lodash"
import dagre from "dagre"
import {getTextSize} from "@/utils/Layout"
import * as d3 from "d3"
import assert from "assert"

export class SketchNodeSimpleMeta {
  /** @type {SketchNode} */
  sketchNode

  x
  y
  height
  width

  rank

  init(sketchNode) {
    this.sketchNode = sketchNode
  }
}

export class SketchEdgeSimpleMeta {
  /** @type {SketchEdge} */
  sketchEdge

  points
  path

  init(sketchEdge) {
    this.sketchEdge = sketchEdge
  }
}

export class SketchGraphSimpleMeta {
  /** @type {SketchGraph} */
  sketchGraph

  /** @type {TimelineRow[]} */
  timelineRows = []

  /** @type {number} */
  height
  /** @type {number} */
  width
  /** @type {SketchNodeSimpleMeta[]} */
  nodeMetas = []
  /** @type {SketchEdgeSimpleMeta[]} */
  edgeMetas = []

  toAlign = true

  /**
   * @param {SketchGraph} graph
   * @param {Plan[]} plans
   */
  init(graph, plans) {
    this.sketchGraph = graph

    for (const node of graph.nodes) {
      const tl = new TimelineRow()
      tl.init(node, plans)
      this.timelineRows.push(tl)
    }

    this.nodeMetas = this.sketchGraph.nodes.map(v => v.createSimpleMeta())
    this.edgeMetas = this.sketchGraph.edges.map(e => e.createSimpleMeta())
  }

  layout(conf) {
    this.layoutTimelineRows(conf)
    this.layoutOverviewGraph(conf)
  }

  /**
   * @param {SketchNodeSimpleMeta} meta
   */
  getRowByMeta(meta) {
    return _.find(this.timelineRows, r => r.sketchNode === meta.sketchNode)
  }

  // eslint-disable-next-line no-unused-vars
  layoutTimelineRows(conf) {
    this.timelineRows.forEach(row => row.layout())
    // compute align width for each timeline item
    for (let i = 0; i < this.timelineRows[0].timelineItems.length; i++) {
      const alignWidth = _.max(this.timelineRows.map(row => row.timelineItems[i].width))
      this.timelineRows.forEach(row => row.timelineItems[i].alignWidth = alignWidth)
    }
  }

  layoutOverviewGraph(conf) {
    const nodePaddingX = conf?.nodePaddingX ?? 10
    const nodePaddingY = conf?.nodePaddingY ?? 5
    const marginX = conf?.merginX ?? 10
    const marginY = conf?.merginY ?? 10
    const fontSize = conf?.fontSize ?? 20

    this.computeRank()

    let g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir: 'BT',
      ranksep: conf?.ranksep ?? '10',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.sketchGraph.nodes.forEach(node => {
      const {width, height} = getTextSize(node.type, fontSize)
      node.simpleMeta.width = width + nodePaddingX
      node.simpleMeta.height = height + nodePaddingY
      g.setNode(node.vid, node.simpleMeta)
    })

    this.sketchGraph.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        const minLen = edge.src.simpleMeta.rank - edge.dst.simpleMeta.rank
        console.log(edge, minLen)
        g.setEdge({v: edge.src.vid, w: edge.dst.vid}, {minlen: minLen})
      })
    })

    dagre.layout(g)

    this.g = g

    // overwrite y
    let yPtr = 10 + 30;
    ([...this.nodeMetas]).sort(m => m.rank)
        .forEach(meta => {
          const row = this.getRowByMeta(meta)
          meta.y = yPtr + row.height / 2
          yPtr += row.height + 40 + 30
        })

    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.sketchGraph.nodes.forEach(node => {
      node.inEdges.forEach(edge => {
        const points = g.edge({v: edge.src.vid, w: edge.dst.vid}).points
        // overwrite y
        const scale = d3.scaleLinear(d3.extent(points.map(p => p.y)),
            [edge.dst.simpleMeta.y, edge.src.simpleMeta.y])
        points.forEach(p => p.y = scale(p.y))
        edge.simpleMeta.points = points
        edge.simpleMeta.path = lineGen(points)
      })
    })

    // compute total size
    this.width = Math.max(...this.nodeMetas.map(meta => {
      return meta.x + meta.width / 2
    })) + marginX * 2
    this.height = Math.max(...this.nodeMetas.map(meta => {
      return meta.y + meta.height / 2
    })) + marginY * 2
  }

  computeRank() {
    const roots = this.sketchGraph.nodes.filter(v => v.outEdges.length === 0)
    assert(roots.length === 1)
    const root = roots[0]

    let rankCnt = 0
    const dfs = function(node) {
      node.simpleMeta.rank = rankCnt
      rankCnt += 1
      node.inEdges.forEach(e => dfs(e.src))
    }
    dfs(root)
  }
}
