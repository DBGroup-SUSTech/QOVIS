import {QuestionList} from "@/js/question/questionList"
import {Problem} from "@/js/question/Problem"

const Orders = [
    ['qv', 'qvm', 'nm', 'qv', 'qvm', 'nm',  'qv',   'nm', 'qvm',],
    ['qv', 'nm', 'qvm', 'qv', 'nm', 'qvm',  'qv',  'qvm', 'nm', ],
    ['qvm', 'qv', 'nm', 'qvm', 'qv', 'nm',  'qvm',  'nm',  'qv',],
    ['qvm', 'nm', 'qv', 'qvm', 'nm', 'qv',  'qvm',  'qv',  'nm',],
    ['nm', 'qv', 'qvm', 'nm', 'qv', 'qvm',  'nm',  'qvm', 'qv', ],
    ['nm', 'qvm', 'qv', 'nm', 'qvm', 'qv',  'nm',   'qv', 'qvm',]
]

export const Methods = ['qv', 'qvm', 'nm']

class ProblemGen {
  problems = []

  constructor() {
    this._generateAllProblems()
  }

  _generateAllProblems() {
    this.problems = []
    let id = 0
    QuestionList.forEach(question => {
      for (const method of Methods) {
        this.problems.push(new Problem(id++, method, question))
      }
    })
  }

  getProblems(orderSeed) {
    const problems = []
    for (let i = 0; i < QuestionList.length; i++) {
      const problemCandidates = this.problems.slice(i * Methods.length, (i + 1) * Methods.length)
      const selectedIdx = Methods.indexOf(this.getMethod(orderSeed, i))
      const problem = problemCandidates[selectedIdx]
      problems.push(problem.instantiate())
    }
    return problems
  }

  getProblemsDev() {
    return this.problems.map(problem => problem.instantiate())
  }

  /**
   * @param orderSeed
   * @param idx
   * @returns {string}
   */
  getMethod(orderSeed, idx) {
    console.log('orderSeed', orderSeed ,Orders)
    const baseOrder = Orders[orderSeed % Orders.length]
    return baseOrder[idx % baseOrder.length]
  }
}

export const problemGen = new ProblemGen()
