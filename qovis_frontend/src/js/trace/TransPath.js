import {VisTransPath} from "@/js/trace/VisTransPath"
import {TransLink} from "@/js/trace/TransLink"

export class TransPath {
  /** @type {QueryPlan} */
  srcPlan
  /** @type {QueryPlan} */
  dstPlan
  /** @type {boolean} */
  success     // has no meaning for now
  /** @type {string[]} */
  rulePath
  /** @type {TransLink[]} */
  links

  /** @type {VisTransPath} */
  visObj = null

  /**
   * @param {QueryPlan} srcPlan
   * @param {QueryPlan} dstPlan
   * @param {boolean} success
   * @param {string[]} rulePath
   * @param {Object[]} links
   * @return {TransPath}
   */
  init(srcPlan, dstPlan, success, rulePath, links) {
    this.srcPlan = srcPlan
    this.dstPlan = dstPlan
    this.success = success
    this.rulePath = rulePath

    this.links = links.map(link => {
      return new TransLink(
          srcPlan.nodeMap.get(link.vid0),
          dstPlan.nodeMap.get(link.vid1),
          link.kind,
          link.p0,
          link.p1,
          link.idx0,
          link.idx1,
          link.rules)
    })
    return this
  }

  /**
   * @returns {VisTransPath}
   */
  createVisObj() {
    this.visObj = new VisTransPath(this)
    return this.visObj
  }
}

