import {VisTransform} from "@/js/probe/VisTransform"

/**
 * @enum {string}
 * @readonly
 */
export const TransType = {
  INSERT: 'insert',
  DELETE: 'delete',
  REPLACE: 'replace',
  MODIFY: 'modify',
  UNCHANGE: 'unchange',
}

export class Transform {
  /** @type {VisTransform} */
  visObj = null

  srcVid
  dstVid
  /** @type {TransType} */
  type

  /**
   * @param {int | null} srcVid
   * @param {int | null} dstVid
   * @param {TransType} type
   */
  constructor(srcVid, dstVid, type) {
    this.srcVid = srcVid
    this.dstVid = dstVid
    this.type = type
  }

  createVisObj() {
    this.visObj = new VisTransform(this)
    return this.visObj
  }

  static load(data) {
    return new Transform(
      data.srcVid,
      data.dstVid,
      data.type,
    )
  }

  toString() {
    return `${this.type} ${this.srcVid} -> ${this.dstVid}`
  }
}
