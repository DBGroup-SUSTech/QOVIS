export class OptInfo {
  name
  type
  alias
  isImp

  init({name, type, alias, isImp}) {
    this.name = name
    this.type = type
    this.alias = alias
    this.isImp = isImp
    return this
  }
}
