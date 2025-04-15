export class IdCounter {
  _id

  constructor(start=0) {
    this._id = start - 1
  }

  get() {
    this._id += 1
    return this._id
  }

  // update(curId) {
  //   if (curId > this._id) {
  //     this._id = curId
  //   }
  // }

  set(id) {
    this._id = id
  }
}
