export class VisNode {
  /** @type {VisGraph} */
  visGraph

  /** @type {int} */
  vid
  /** @type {VisNode[]} */
  inNodes = []
  /** @type {VisNode[]} */
  outNodes = []

  /** @type {VisPlan[]} */
  visPlans = []
  /** @type {VisTran[]} */
  visTrans = []

  x
  y
  width
  height

  layout(conf) {
    const padding = 10
    this.visPlans.forEach(p => p.layout(conf))
    this.visTrans.forEach(t => t.layout(conf))

    this.height = Math.max(0, ...this.visPlans.map(p => p.height)) + padding * 2

    let curX = padding
    for (let i = 0; i < this.visPlans.length; i++) {
      const p = this.visPlans[i]
      p.x = curX + p.width / 2
      p.y = this.height / 2
      curX += p.width + padding

      if (i !== this.visPlans.length - 1) {
        const t = this.visTrans[i]
        t.x = curX + padding
        t.y = p.y
        curX += t.width + padding
      }
    }

    this.width = curX

  }
}
