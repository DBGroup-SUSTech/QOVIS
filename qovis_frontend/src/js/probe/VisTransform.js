// eslint-disable-next-line no-unused-vars
import {TransType, Transform} from "@/js/probe/Transform"
import * as d3 from "d3"


export class VisTransform {
  /** @type {Transform} */
  origin = null

  /** @type {VisQueryPlan} */
  srcPlan
  /** @type {VisQueryPlan} */
  dstPlan

  /** @type {{x: number, y: number}[]} */
  points = []
  /** @type {string} */
  path = ''
  /** @type {string} */
  color = 'red'

  constructor(origin) {
    this.origin = origin
  }

  /**
   * @param {VisQueryPlan} srcPlan
   * @param {VisQueryPlan} dstPlan
   * @returns {VisTransform}
   */
  init(srcPlan, dstPlan) {
    this.srcPlan = srcPlan
    this.dstPlan = dstPlan
    return this
  }

  /**
   * @param {ConfigV3} config
   */
  // eslint-disable-next-line no-unused-vars
  layout(config) {
    if (this.origin.srcVid == null || this.origin.dstVid == null) {
      return
    }

    const srcPlanX = this.srcPlan.x
    const srcPlanY = this.srcPlan.y
    const dstPlanX = this.dstPlan.x
    const dstPlanY = this.dstPlan.y

    const srcPlanNode = this.srcPlan.nodeMap.get(this.origin.srcVid)
    const dstPlanNode = this.dstPlan.nodeMap.get(this.origin.dstVid)

    const startX = srcPlanX + srcPlanNode.x + srcPlanNode.width
    const startY = srcPlanY + srcPlanNode.y + srcPlanNode.height / 2
    const endX = dstPlanX + dstPlanNode.x
    const endY = dstPlanY + dstPlanNode.y + dstPlanNode.height / 2
    this.points = [
      {x: startX, y: startY},
      {x: startX + (endX - startX) / 3, y: startY + (endY - startY) / 5},
      {x: endX - (endX - startX) / 3, y: endY - (endY - startY) / 5},
      {x: endX, y: endY},
    ]
    const lineGen = d3.line().x(p => p.x).y(p => p.y).curve(d3.curveBasis)
    this.path = lineGen(this.points)

    switch(this.origin.type) {
      case TransType.INSERT: this.color = 'green'; break
      case TransType.DELETE: this.color = 'red'; break
      case TransType.REPLACE: this.color = '#de8344'; break
      case TransType.MODIFY: this.color = '#f5c242'; break
      case TransType.UNCHANGE: this.color = '#cccccc'; break
    }
  }
}
