import {Edge} from "@/js/common/Graph"

/**
 * @extends {Edge<VisPlanNode, VisPlanEdge>}
 */
export class VisPlanEdge extends Edge {
  /** @type {{x: int, y: int}[]} */
  points = []

  textX = 0
  textY = 0

  constructor() {
    super()
  }

  toString() {
    return this.origin?.toString() ?? ""
  }

  get link() {
    return ''
  }

  get planEdgeStr() {
    let str = this.link
    if (str.includes(':')) {
      str = str.split(':')[1]
    }
    if (str.includes('exists')) {
      str = 'Exists'
    }
    return str
  }
}
