const svg = document.createElementNS('http://www.w3.org/2000/svg','svg')
const text = document.createElementNS('http://www.w3.org/2000/svg','text')
svg.append(text)

export function getTextSize(str, fontSize, fontFamily) {
  document.body.append(svg)
  if (fontSize) {
    text.setAttribute('font-size', fontSize)
  }
  if (fontFamily) {
    text.setAttribute('font-family', fontFamily)
  }
  text.innerHTML = str
  const {width, height} = text.getBBox()
  document.body.removeChild(svg)
  return {width, height}
}

export function getTextBoundingSize(str, {fontSize, fontFamily, rotate} = {}) {
  document.body.append(svg)
  if (fontSize) {
    text.setAttribute('font-size', fontSize)
  }
  if (fontFamily) {
    text.setAttribute('font-family', fontFamily)
  }
  if (rotate) {
    text.setAttribute('transform', `rotate(${rotate})`)
  }
  text.innerHTML = str
  const {width, height} = text.getBoundingClientRect()
  document.body.removeChild(svg)

  return {width, height}
}

export function getLimitedString(str, widthLimit, fontSize) {
  let {width} = str ? getTextSize(str, fontSize) : {width: 0}
  if (width < widthLimit) {
    return str
  }

  let {width: extraWidth} = getTextSize("...", fontSize)
  let tempWidth = width
  while (tempWidth > widthLimit - extraWidth) {
    str = str.slice(0, -1)
    const ret = getTextSize(str, fontSize)
    tempWidth = ret.width + extraWidth
  }
  return str + "..."
}

/**
 * @param {SVGSVGElement} svg
 * @param {SVGGraphicsElement} element
 * @returns {{x: number, y: number}}
 */
export function getPosition(svg, element) {
  const rootPoint = svg.createSVGPoint()
  const ctm = element.getCTM()
  const elPoint = rootPoint.matrixTransform(ctm)
  return {x: elPoint.x, y: elPoint.y}
}
