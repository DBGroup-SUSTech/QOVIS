export class Question {
  caseName
  task
  /** @type {string} */
  description

  /** @type {string} */
  head
  /** @type {{id: number, text: string}[]} */
  options
  /** @type {number} */
  correctOptionId

  constructor(caseName, task, description, head, options, correctOptionId) {
    this.caseName = caseName
    this.task = task
    this.description = description
    this.head = head
    this.options = options
    this.correctOptionId = correctOptionId
  }
}
