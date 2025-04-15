export class Answer {
  questionId
  task
  caseName
  method

  answerCount
  startTime
  endTime

  selectionList     // 0-3, option id
  selReasonList     // strings
  confidenceList    // 1-5
  timeList          // time used for each selection

  _lastTime
  _isFinished = false

  constructor(questionId, task, caseName, method) {
    this.questionId = questionId
    this.task = task
    this.caseName = caseName
    this.method = method

    this.answerCount = 0
    this.startTime = 0
    this.endTime = 0

    this._isFinished = false

    this.selectionList = []
    this.selReasonList = []
    this.confidenceList = []
    this.timeList = []
  }

  startAnswer() {
    this.startTime = new Date().getTime()
    this._lastTime = this.startTime
  }

  endAnswer() {
    this._isFinished = true
    this.endTime = new Date().getTime()
  }

  addAnswer(selection, confidence, reason) {
    if (this._isFinished) {
      return
    }
    this.selectionList.push(selection)
    this.confidenceList.push(confidence)
    this.selReasonList.push(reason)

    const currentTime = new Date().getTime()
    this.timeList.push(currentTime - this._lastTime)
    this._lastTime = currentTime

    this.answerCount++
  }

  toJson() {
    return {
      questionId: this.questionId,
      task: this.task,
      caseName: this.caseName,
      method: this.method,

      answerCount: this.answerCount,
      startTime: this.startTime,
      endTime: this.endTime,
      selectionList: this.selectionList,
      selReasonList: this.selReasonList,
      confidenceList: this.confidenceList,
      timeList: this.timeList,
    }
  }
}
