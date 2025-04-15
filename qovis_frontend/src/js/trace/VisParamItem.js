import {getLimitedString, getTextSize} from "@/utils/Layout"

export class VisParamItem {
  static curID = 0

  /** @type {ParamItem} */
  origin

  id = 1
  text = ''

  /** @type {VisTransLink[]} */
  prevLinks = []
  /** @type {VisTransLink[]} */
  nextLinks = []
  isEqPrev = false
  isEqNext = false

  x = 0
  y = 0
  width = 0
  height = 0
  color = '#000000'

  // interaction
  fixed = false
  isHighlight = false
  isFixHighlight = false

  constructor(origin) {
    this.origin = origin
    this.id = VisParamItem.curID++
  }

  toString() {
    return this.origin.toString()
  }

  get node() {
    return this.origin.node
  }

  get content() {
    // hack 't -> t
    let str = this.origin.content.replaceAll("'", '')
    return str
    // return this.origin.content
  }

  get paramKind() {
    return this.origin.paramKind
  }

  get paramIdx() {
    return this.origin.paramIdx ?? 0    // todo: fix bug
  }

  /**
   * Must be called after prevTransPath and nextTransPath are set.
   * @param {VisQueryPlan} plan
   */
  initLinks(plan) {
    this.prevLinks = []
    this.nextLinks = []
    if (plan.prevTransPath) {
      plan.prevTransPath.dstVid2Links.get(this.node.vid).forEach(link => {
        if (link.connectTo(this)) {
          this.prevLinks.push(link)
        }
      })
    }
    if (plan.nextTransPath) {
      plan.nextTransPath.srcVid2Links.get(this.node.vid).forEach(link => {
        if (link.connectFrom(this)) {
          this.nextLinks.push(link)
        }
      })
    }

    if (this.prevLinks.length === 1 && this.prevLinks[0].origin.kind === 'eq') {
      this.isEqPrev = true
    }
    if (this.nextLinks.length === 1 && this.nextLinks[0].origin.kind === 'eq') {
      this.isEqNext = true
    }
  }

  layout(maxWidth, textPadding, fontSize) {
    let str = this.content.slice(0, maxWidth / fontSize * 2.5)    // 2.5 is a magic number. char count for 1 line.
    this.text = getLimitedString(str, maxWidth - 2 * textPadding, fontSize)
    const {width, height} = getTextSize(this.text.replace('<', '&lt;'), fontSize)
    this.width = width + 2 * textPadding
    this.height = height
  }

  highlight() {
    this.highlightForwardIterative()
    this.highlightBackwardIterative()
  }

  unhighlight() {
    this.unhighlightForwardIterative()
    this.unhighlightBackwardIterative()
  }

  highlightForwardIterative() {
    this.isHighlight = true

    const {links, items} = this.getAllPrev()
    links.forEach(link => {
      link.isHighlight = true
    })
    items.forEach(item => {
      item.isHighlight = true
    })
  }

  unhighlightForwardIterative() {
    this.isHighlight = false

    const {links, items} = this.getAllPrev()
    links.forEach(link => {
      link.isHighlight = false
    })
    items.forEach(item => {
      item.isHighlight = false
    })
  }

  getAllPrev() {
    const linkSet = new Set(this.prevLinks)
    const itemSet = new Set()
    let links = this.prevLinks
    let items = []
    while (links.length > 0) {
      // collect items from links
      items = []
      links.forEach(link => {
        items.push(link.srcItem)
        itemSet.add(link.srcItem)
      })
      items = Array.from(new Set(items))  // unique items
      // collect links from items
      links = []
      items.forEach(item => {
        item.prevLinks.forEach(link => {
          links.push(link)
          linkSet.add(link)
        })
      })
      links = Array.from(new Set(links))  // unique links
    }

    return {
      links: Array.from(linkSet),
      items: Array.from(itemSet),
    }
  }

  highlightBackwardIterative() {
    this.isHighlight = true

    const {links, items} = this.getAllNext()
    links.forEach(link => {
      link.isHighlight = true
    })
    items.forEach(item => {
      item.isHighlight = true
    })
  }

  unhighlightBackwardIterative() {
    this.isHighlight = false

    const {links, items} = this.getAllNext()
    links.forEach(link => {
      link.isHighlight = false
    })
    items.forEach(item => {
      item.isHighlight = false
    })
  }

  getAllNext() {
    const linkSet = new Set(this.nextLinks)
    const itemSet = new Set()
    let links = this.nextLinks
    let items = []
    while (links.length > 0) {
      // collect items from links
      items = []
      links.forEach(link => {
        items.push(link.dstItem)
        itemSet.add(link.dstItem)
      })
      items = Array.from(new Set(items))  // unique items
      // collect links from items
      links = []
      items.forEach(item => {
        item.nextLinks.forEach(link => {
          links.push(link)
          linkSet.add(link)
        })
      })
      links = Array.from(new Set(links))  // unique links
    }

    return {
      links: Array.from(linkSet),
      items: Array.from(itemSet),
    }
  }

  fixHighlight() {
    this.fixed = true
    this.fixHighlightForwardIterative()
    this.fixHighlightBackwardIterative()
  }

  unfixHighlight() {
    this.fixed = false
    this.unfixHighlightForwardIterative()
    this.unfixHighlightBackwardIterative()
  }

  fixHighlightForwardIterative() {
    this.isFixHighlight = true

    const {links, items} = this.getAllPrev()
    links.forEach(link => {
      link.isFixHighlight = true
    })
    items.forEach(item => {
      item.isFixHighlight = true
    })
  }

  unfixHighlightForwardIterative() {
    this.isFixHighlight = false

    const {links, items} = this.getAllPrev()
    links.forEach(link => {
      link.isFixHighlight = false
    })
    items.forEach(item => {
      item.isFixHighlight = false
    })
  }

  fixHighlightBackwardIterative() {
    this.isFixHighlight = true

    const {links, items} = this.getAllNext()
    links.forEach(link => {
      link.isFixHighlight = true
    })
    items.forEach(item => {
      item.isFixHighlight = true
    })
  }

  unfixHighlightBackwardIterative() {
    this.isFixHighlight = false

    const {links, items} = this.getAllNext()
    links.forEach(link => {
      link.isFixHighlight = false
    })
    items.forEach(item => {
      item.isFixHighlight = false
    })
  }

  getPrevChItem() {
    if (!this.isEqPrev) {
      return null
    }
    const prevItem = this.prevLinks[0].srcItem
    return prevItem.isEqPrev ? prevItem.getPrevChItem() : prevItem
  }

  getNextChItem() {
    if (!this.isEqNext) {
      return null
    }
    const nextItem = this.nextLinks[0].dstItem
    return nextItem.isEqNext ? nextItem.getNextChItem() : nextItem
  }
}
