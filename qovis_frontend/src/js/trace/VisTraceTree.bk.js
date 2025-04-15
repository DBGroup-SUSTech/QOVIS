import assert from "assert"
import * as d3 from "d3"
// eslint-disable-next-line no-unused-vars
import {PlanBlock} from "@/js/trace/PlanBlock"
import {TransPath} from "@/js/trace/TransPath"

// comment contains old tree alignment result visualization

export class VisTraceTree {
  /** @type {TraceTree} */
  origin

  /** @type {VisTraceNode} */
  root
  /** @type {PlanBlock[]} */
  planBlocks = []

  /** @type {Map<string, number>} */
  colorMap = new Map()
  color = d3.scaleOrdinal(d3.schemeCategory10.concat(d3.schemeAccent))

  /** @type {VisTraceNode[]} */
  selectedNodes = []
  /** @type {(VisQueryPlan | null)[]} */
  visPlans = []    // size = size of selectedNodes + 1. this is a cache for all visPlans

  /** @type {VisTransPath[]} */
  visTransPaths = []

  /** @type {d3.scaleLinear} */
  stepCntScale = d3.scaleLinear().domain([0, 1]).range([0, 1])

  // layout
  width = 0
  height = 0
  startX = 0
  startY = 0

  maxLevel = 0
  planDagStartY = 0

  /**
   * @param {TraceTree} traceTree
   */
  constructor(traceTree) {
    this.origin = traceTree
  }

  /**
   * @param {ConfigV3} config
   */
  // eslint-disable-next-line no-unused-vars
  init(config) {
    const {maxBarHeight, minBarHeight} = config.nav
    this.stepCntScale
        .domain([1, this.origin.maxFirstLevelStepCnt])
        .range([minBarHeight, maxBarHeight])

    this.selectedNodes = []
    this.visPlans = this.origin.trace.plans.map(() => null)

    // init root
    this.root = this.origin.root.createVisObj()
    this.root.init(null)
    this.root.setExpanded(true)

    this.root.initLevel(0)

    console.log(this.root)
  }

  /**
   * @param {ConfigV3} config
   */
  initialLayout(config) {
    this.updateNavLayout(config)
    this.root.initialLayout(config, 0)
    this.initPlanBlocks(config)
    this.initTransforms()
    this.updateLayout(config)
    this.initColorMap()
  }

  updateNavLayout(config) {
    const {rowHeight, planDagMarginTop} = config.nav
    this.selectedNodes = this.getSelectedNodes()
    this.maxLevel = this.selectedNodes.reduce((acc, cur) => Math.max(acc, cur.level), 0)
    this.planDagStartY = this.maxLevel * rowHeight + planDagMarginTop
  }

  /**
   * @param {ConfigV3} config
   */
  initPlanBlocks(config) {
    const {rowHeight, blockRadius} = config.nav

    const visPlans = [this.selectedNodes[0].startVisPlan, ...this.selectedNodes.map(node => node.endVisPlan)]
    this.planBlocks = visPlans.map((visPlan, i) => new PlanBlock(this, this.root, i, visPlan))

    /* compute layout of each block rect */

    const firstBlock = this.planBlocks[0]
    const firstNode = this.selectedNodes[0]
    firstBlock.centerX = 0
    firstBlock.topY = 0
    firstBlock.radius = blockRadius
    firstBlock.rectHeight = rowHeight * (firstNode.level - 1)

    for (let i = 1; i < this.planBlocks.length - 1; i++) {
      const leftNode = this.selectedNodes[i - 1]
      const rightNode = this.selectedNodes[i]
      const planBlock = this.planBlocks[i]

      // find the common ancestor of leftNode and rightNode
      const ancestor = this.getCommonAncestor(leftNode, rightNode)

      planBlock.centerX = rightNode.x
      planBlock.topY = ancestor.y + rowHeight   // start at the row below the common ancestor
      planBlock.radius = blockRadius
      planBlock.rectHeight = rowHeight * (Math.max(leftNode.level, rightNode.level) - ancestor.level - 1)
    }

    const lastBlock = this.planBlocks[this.planBlocks.length - 1]
    const lastNode = this.selectedNodes[this.selectedNodes.length - 1]
    lastBlock.centerX = this.root.x + this.root.width
    lastBlock.topY = 0
    lastBlock.radius = blockRadius
    lastBlock.rectHeight = rowHeight * (lastNode.level - 1)

    // initial layout of visPlan
    for (const planBlock of this.planBlocks) {
      const visPlan = planBlock.visPlan
      visPlan.y = this.planDagStartY
      visPlan.x = planBlock.centerX - visPlan.width / 2
    }

    // compute change label
    // visPlans.forEach(dag => dag.nodes.forEach(node => node.evoLabels = []))
    // for (let i = 0; i < visPlans.length - 1; i++) {
    //   const vp0 = visPlans[i], vp1 = visPlans[i + 1]
    //   const addrMap0 = new Map(vp0.nodes.map(node => [node.origin.addr, node]))
    //   const addrMap1 = new Map(vp1.nodes.map(node => [node.origin.addr, node]))
    //   const addrList0 = Array.from(addrMap0.keys())
    //   const addrList1 = Array.from(addrMap1.keys())
    //
    //   const added = _.difference(addrList1, addrList0)
    //   for (const addr of added) {
    //     addrMap1.get(addr).evoLabels.push('added')
    //   }
    //
    //   const toRemove = _.difference(addrList0, addrList1)
    //   for (const addr of toRemove) {
    //     addrMap0.get(addr).evoLabels.push('to_remove')
    //   }
    // }
  }

  initTransforms() {
    // const visPlans = this.planBlocks.map(block => block.visPlan)
    // const planIdList = this.origin.trace.plans.map(plan => plan.pid)
    //
    // const visTransPaths = []
    // for (let i = 0; i < visPlans.length - 1; i++) {
    //   const vp0 = visPlans[i], vp1 = visPlans[i + 1]
    //   const id1 = vp0.origin.pid, id2 = vp1.origin.pid
    //   const idx1 = planIdList.indexOf(id1), idx2 = planIdList.indexOf(id2)
    //   if (Math.abs(idx1 - idx2) === 1) {
    //     // adjacent
    //     const transPath = this.origin.trace.transforms[idx1]
    //     const visTransPath = transPath.createVisObj().init()
    //     visTransPaths.push(visTransPath)
    //   }
    // }
    // this.visTransPaths = visTransPaths

    const visPlans = this.planBlocks.map(block => block.visPlan)
    const planIdList = this.origin.trace.plans.map(plan => plan.pid)

    const visTransPaths = []
    for (let i = 0; i < visPlans.length - 1; i++) {
      const vp0 = visPlans[i], vp1 = visPlans[i + 1]
      const id1 = vp0.origin.pid, id2 = vp1.origin.pid
      const idx1 = planIdList.indexOf(id1), idx2 = planIdList.indexOf(id2)
      if (Math.abs(idx1 - idx2) === 1) {
        // adjacent
        const transPath = this.origin.trace.transforms[idx1]
        // console.log(idx1)
        const visTransPath = transPath.createVisObj().init()
        visTransPaths.push(visTransPath)
      } else {
        const subTransPaths = this.origin.trace.transforms.slice(idx1, idx2)
        const success = subTransPaths.every(tp => tp.success)
        const rulePath = success ? subTransPaths.flatMap(tp => tp.rulePath) : []
        let links = []
        if (success) {
          links = subTransPaths[0].links
          for (let i = 1; i < subTransPaths.length; i++) {
            links = this.mergeRuleStepLinks(links, subTransPaths[i].links)
          }
        }
        const transPath = new TransPath().init(vp0.origin, vp1.origin, success, rulePath, [])
        transPath.links = links
        const visTransPath = transPath.createVisObj().init()
        visTransPaths.push(visTransPath)
        // console.log(this.origin.trace.transforms, idx1, idx2, subTransPaths)
        // console.log('merge', visTransPath, subTransPaths.map(tp => tp.links), links, this)
      }
    }
    this.visTransPaths = visTransPaths
  }

  /**
   * @param {TransLink[]} links1
   * @param {TransLink[]} links2
   */
  mergeRuleStepLinks(links1, links2) {
      // python code
      // # t0 -> t1 -> t2
      // # (vid (in t1), param name, param idx) -> links
      //   links0_dict: dict[tuple[int, str, int], list[TransLink]] = {}
      //   for link in links0:
      //   key = (link.node1.vid, link.param1, link.param_idx1)
      //   links0_dict.setdefault(key, []).append(link)
      //   links1_dict: dict[tuple[int, str, int], list[TransLink]] = {}
      //   for link in links1:
      //   key = (link.node0.vid, link.param0, link.param_idx0)
      //   links1_dict.setdefault(key, []).append(link)
      //
      //   result_links = []
      //   for key, links in links0_dict.items():
      //   if key not in links1_dict:
      //   continue
      //   links_tmp = links1_dict[key]
      //   for link0 in links:
      //   for link1 in links_tmp:
      //   new_link = link0.merge(link1)
      //   result_links.append(new_link)
      //
      //   return result_links

    const links1Map = new Map()
    for (const link of links1) {
      const key = [link.node1.vid, link.param1, link.paramIdx1].join(',')
      links1Map.set(key, links1Map.has(key) ? links1Map.get(key).concat(link) : [link])
    }
    const links2Map = new Map()
    for (const link of links2) {
      const key = [link.node0.vid, link.param0, link.paramIdx0].join(',')
      links2Map.set(key, links2Map.has(key) ? links2Map.get(key).concat(link) : [link])
    }

    const resultLinks = []
    for (const [key, links] of links1Map.entries()) {
      if (!links2Map.has(key)) {
        continue
      }
      const linksTmp = links2Map.get(key)
      for (const link0 of links) {
        for (const link1 of linksTmp) {
          const newLink = link0.merge(link1)
          console.assert(newLink.node0 !== null && newLink.node1 !== null)
          resultLinks.push(newLink)
        }
      }
    }

    return resultLinks
  }

  /**
   * @param {VisTraceNode} leftNode
   * @param {VisTraceNode} rightNode
   * @returns {VisTraceNode}
   */
  getCommonAncestor(leftNode, rightNode) {
    const leftPath = []
    let node = leftNode
    while (node !== null) {
      leftPath.push(node)
      node = node.parent
    }
    const rightPath = []
    node = rightNode
    while (node !== null) {
      rightPath.push(node)
      node = node.parent
    }
    // find the joint node of leftPath and rightPath
    let i = 0, j = 0
    let paths = [leftPath, rightPath]
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const x = paths[0][i]
      const y = paths[1][j]
      if (x === y) {
        return x
      }
      if (i >= paths[0].length - 1) {
        // paths[0] is leftPath
        paths[0] = rightPath
        i = 0
      } else {
        i += 1
      }
      if (j >= paths[1].length - 1) {
        // paths[1] is rightPath
        paths[1] = leftPath
        j = 0
      } else {
        j += 1
      }
    }
  }

  initColorMap() {
    let idx = 0
    const collectColor = (node) => {
      const name = node.getSimpleName()
      if (!this.colorMap.has(name)) {
        this.colorMap.set(name, idx++)
      }
      for (const child of node.children) {
        collectColor(child)
      }
    }

    collectColor(this.root)
  }

  getColor(node) {
    const name = node.getSimpleName()
    const idx = this.colorMap.get(name)
    return this.color(idx % 10)
  }

  /**
   * @param {ConfigV3} config
   */
  // eslint-disable-next-line no-unused-vars
  updateLayout(config) {
    const {margin} = config.plan

    this.width = this.root.width
        + this.planBlocks[0].visPlan.width / 2
        + this.planBlocks[this.planBlocks.length - 1].visPlan.width / 2
        + margin * 2
    this.height = this.planBlocks.reduce((acc, cur) => Math.max(acc, cur.visPlan.y + cur.visPlan.height), 0)
        + margin
    this.startX = margin + this.planBlocks[0].visPlan.width / 2
    this.startY = 0

    this.visTransPaths.forEach(transPath => {
      if (transPath === null) {
        return
      }
      transPath.layout(config)
    })
  }

  getSelectedNodes() {
    const nodes = []
    const collect = (node) => {
      if (!node.expanded) {
        nodes.push(node)
      } else {
        for (const child of node.children) {
          collect(child)
        }
      }
    }
    collect(this.root)
    return nodes
  }

  getVisPlan(idx) {
    assert(idx >= 0 && idx < this.visPlans.length, 'Invalid idx ' + idx)
    let visPlan = this.visPlans[idx]
    if (visPlan === null) {
      const plan = this.origin.trace.plans[idx]
      visPlan = plan.createVisObj()
      this.visPlans[idx] = visPlan
    }
    return visPlan
  }

  /**
   * @param {ConfigV3} config
   * @param {VisTraceNode} node
   */
  toggleTraceNode(config, node) {
    node.setExpanded(!node.expanded)
    // temp
    this.updateNavLayout(config)
    this.root.initialLayout(config, 0)
    this.initPlanBlocks(config)
    this.initTransforms()
    this.updateLayout(config)
  }
}

