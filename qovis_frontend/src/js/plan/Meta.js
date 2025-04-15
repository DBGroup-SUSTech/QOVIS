export class Meta {
  /** @type {String} */
  metaType

  type
  name

  constructor(metaType) {
    this.metaType = metaType
  }

  toString() {
    return this.name
  }

  getSimpleName() {
    let name = this.name
    if (name.endsWith("$")) {
      name = name.substring(0, name.length - 1)
    }
    if (name.includes('.')) {
      name = name.split('.')[1]
    }
    if (name.includes("$")) {
      name = name.split("$")[1]
    }
    return name
  }

  static load(obj) {
    switch (obj['metaType']) {
      case 'rule': return RuleMeta.load(obj)
      case 'strategy': return StrategyMeta.load(obj)
      case 'softTrans': return SoftTransMeta.load(obj)
      case 'action': return ActionMeta.load(obj)
    }
    throw Error('Unknown meta type: ' + obj['metaType'])
  }

  getInfoPairs() {
    return []
  }

  getPhaseName() {
    switch (this.type) {
      case 'analysis rule': return 'Analysis'
      case 'optimizer rule': return 'Optimization'
      case 'execution rule': return 'Execution'
      case 'strategy': return 'Planning'
      case 'soft trans': return 'Transform'
      case 'opt': return 'Action'
    }
    return 'Unknown'
  }
}

export class RuleMeta extends Meta {
  type
  name
  runTime
  className

  batchName
  batchId

  constructor() {
    super('rule')
  }

  static load(raw) {
    return Object.assign(new RuleMeta(), raw)
  }

  getInfoPairs() {
    const pairs = super.getInfoPairs()
    for (const k of ['type', 'name', 'runTime', 'className', 'batchName', 'batchId']) {
      pairs.push([k, this[k]])
    }
    return pairs
  }
}

export class StrategyMeta extends Meta {
  type
  name
  runTime
  className

  invokeCnt
  rid

  constructor() {
    super('strategy')
  }

  static load(raw) {
    return Object.assign(new StrategyMeta(), raw)
  }

  getInfoPairs() {
    const pairs = super.getInfoPairs()
    for (const k of ['type', 'name', 'runTime', 'className', 'invokeCnt', 'rid']) {
      pairs.push([k, this[k]])
    }
    return pairs
  }
}

export class SoftTransMeta extends Meta {
  type
  name
  runTime = 0

  constructor() {
    super('softTrans')
  }

  static load(raw) {
    return Object.assign(new SoftTransMeta(), raw, {type: 'soft trans', name: 'SoftTrans'})
  }

  getInfoPairs() {
    const pairs = super.getInfoPairs()
    for (const k of ['type']) {
      pairs.push([k, this[k]])
    }
    return pairs
  }
}

export class ActionMeta extends Meta {
  type
  name
  runTime
  className

  batchName
  batchId

  constructor() {
    super('action')
  }

  static load(raw) {
    return Object.assign(new ActionMeta(), raw)
  }

  getInfoPairs() {
    const pairs = super.getInfoPairs()
    for (const k of ['type', 'name', 'runTime', 'className', 'batchName', 'batchId']) {
      pairs.push([k, this[k]])
    }
    return pairs
  }
}

