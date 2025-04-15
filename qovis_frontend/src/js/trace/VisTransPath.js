export class VisTransPath {
  /** @type {TransPath} */
  origin

  /** @type {VisTransLink[]} */
  links
  /** @type {Map<number, VisTransLink[]>} */
  srcVid2Links = new Map()
  /** @type {Map<number, VisTransLink[]>} */
  dstVid2Links = new Map()

  constructor(origin) {
    this.origin = origin
  }

  /**
   * @returns {VisTransPath}
   */
  init() {
    const srcPlan = this.origin.srcPlan.visObj
    const dstPlan = this.origin.dstPlan.visObj
    this.links = this.origin.links.map(link => link.createVisObj().init(srcPlan, dstPlan))

    this.srcVid2Links = new Map()
    this.dstVid2Links = new Map()
    srcPlan.nodes.forEach(node => this.srcVid2Links.set(node.vid, []))
    dstPlan.nodes.forEach(node => this.dstVid2Links.set(node.vid, []))

    this.links.forEach(link => {
      this.srcVid2Links.get(link.origin.node0.vid).push(link)
      this.dstVid2Links.get(link.origin.node1.vid).push(link)
    })

    return this
  }

  layout(config) {
    this.links.forEach(link => link.layout(config))
  }
}

