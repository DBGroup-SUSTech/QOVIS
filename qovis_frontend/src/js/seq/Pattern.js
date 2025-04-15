export class Pattern {
  /** @type {string} */
  name
  /** @type {"batch" | "phase"} */
  type
  /** @type {PatternItem[]} */
  items = []
}

export class PatternItem {
  /** @type {string} */
  name
  /** @type {"" | "+" | "?" | "*"} */
  desc
}
