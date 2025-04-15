export function getNodeColor(node) {
  switch(node.nodeType) {
    case 'plan': return 'white'
    case 'soft_trans': return '#c6c6c6'
  }
  switch(node.type) {
    case 'analysis rule': return '#adffa7'
    case 'optimizer rule': return '#bfecff'
    case 'strategy': return '#ffe5c4'
      // case 'execution rule': return '#debfff'
    default: return 'black'
  }
}

export function getColor(type) {
  switch (type) {
    case 'analysis rule': return '#9af165'
    case 'optimizer rule': return '#538cf3'
    case 'execution rule': return '#a147ec'
    case 'strategy': return '#ff9046'
    case 'soft trans': return '#bbbbbb'
  }
  console.warn("Can't find color for", type)
  return 'red'
}

export function getFadedColor(type) {
  switch (type) {
    case 'analysis rule': return '#b8ee96'
    case 'optimizer rule': return '#7ea4e5'
    case 'action':
    case 'execution rule': return '#b578e8'
    case 'strategy': return '#fcb384'
    case 'soft trans': return '#bbbbbb'
  }
  console.warn("Can't find color for", type)
  return 'red'
}

export function getEvoTypeColor(type) {
  const addedColor = '#abff98'
  const toRemoveColor = '#ff9696'
  switch (type) {
    case 'A': return addedColor
    case 'R': return toRemoveColor
    case 'U': return '#efefef'
  }
  return 'red'
}
