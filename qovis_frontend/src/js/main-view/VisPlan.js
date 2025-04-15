import dagre from "dagre"
import * as d3 from "d3"
import {getTextSize} from "@/utils/Layout"



export class VisPlanNode {
  /** @type {int} */
  vid
  /** @type {PlanNode} */
  planNode
  /** @type {VisPlanNode[]} */
  children = []

  isEmpty = false

  x
  y
  height
  width

  toAliasStr(alias) {
    return this.isEmpty ? '' : this.planNode.toAlias(alias)
  }

  toString() {
    if (this.isEmpty) {
      return ''
    }
    const str = this.planNode.toString()
    const {width} = getTextSize(str, 20)
    if (width > this.width * 0.9) {
      return str.substring(0, Math.floor(str.length * this.width * 0.85 / width)) + '...'
    } else {
      return str
    }
  }
}

export class VisPlan {
  /** @type {VisPlanNode[]} */
  visPlanNodes = []
  visPlanNodeMap = new Map()

  x
  y
  height
  width

  g

  /**
   * @param {Plan} plan
   * @param {int[]} vidList
   */
  init(plan, vidList) {
    this.plan = plan
    vidList.forEach(vid => {
      const planNode = plan.nodeMap.get(vid)

      const visPlanNode = new VisPlanNode()
      visPlanNode.vid = planNode.vid
      visPlanNode.planNode = planNode

      this.visPlanNodes.push(visPlanNode)
      this.visPlanNodeMap.set(visPlanNode.vid, visPlanNode)
    })

    vidList.forEach(vid => {
      const visPlanNode = this.visPlanNodeMap.get(vid)
      // if (visPlanNode === undefined) {
      //   return
      // }
      visPlanNode.planNode.providers.forEach(p => {
        const child = this.visPlanNodeMap.get(p.vid)
        if (child !== undefined) {
          visPlanNode.children.push(child)
        }
      })
    })

    // this.visPlanNodes.forEach(visPlanNode => {
    //   const planNode = visPlanNode.planNode
    //
    //   planNode.consumers.forEach(c => {
    //     if (this.visPlanNodeMap.has(c.vid)) {
    //       return
    //     }
    //     const fakeNode = new VisPlanNode()
    //     fakeNode.isEmpty = true
    //     fakeNode.vid = planNode.vid
    //
    //     this.visPlanNodes.push(fakeNode)
    //     this.visPlanNodeMap.set(fakeNode.vid, fakeNode)
    //
    //     fakeNode.children.push(visPlanNode)
    //   })
    //
    //   planNode.providers.forEach(p => {
    //     if (this.visPlanNodeMap.has(p.vid)) {
    //       return
    //     }
    //     const fakeNode = new VisPlanNode()
    //     fakeNode.isEmpty = true
    //     fakeNode.vid = planNode.vid
    //
    //     this.visPlanNodes.push(fakeNode)
    //     this.visPlanNodeMap.set(fakeNode.vid, fakeNode)
    //
    //     visPlanNode.children.push(fakeNode)
    //   })
    // })

    return this
  }

  layout(conf) {
    const {useOptAlias} = conf

    if (this.visPlanNodes.length === 0) {
      this.width = 30
      this.height = 15
      return
    }

    let g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir:'BT',
      ranksep: '20',
      nodesep: '10',
    })
    g.setDefaultEdgeLabel(function() {
      return {}
    })

    this.visPlanNodes.forEach(node => {
      // const {width, height} = getTextSize(node.toString())
      let {width, height} = {width: useOptAlias ? 80 : 150, height: 30}
      if (node.isEmpty) {
        width = 15
        height = 15
      }
      node.width = width + 2
      node.height = height + 2
      g.setNode(node.vid, node)
    })

    this.visPlanNodes.forEach(node => {
      node.children.forEach(child => {
        g.setEdge({v: child.vid, w: node.vid})
      })
    })

    dagre.layout(g)

    this.g = g

    // compute total size
    this.width = Math.max(...this.visPlanNodes.map(node => {
      return node.x + node.width / 2
    })) + 5 * 2
    this.height = Math.max(...this.visPlanNodes.map(node => {
      return node.y + node.height / 2
    })) + 5 * 2
  }

  getEdges() {
    const ret = []
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.visPlanNodes.forEach(node => {
      node.children.forEach(child => {
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
