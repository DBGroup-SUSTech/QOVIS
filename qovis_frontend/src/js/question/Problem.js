import {Answer} from "@/js/question/Answer"

export const ToCaseId = {
  'bug0-0': 0,
  'bug4-0': 1,
  'bug1-0': 2,
  'ssb-q1': 3,
  'ssb-q11': 4,
  'bug4-1': 5,
}

export const CaseIdToName = {
  0: 'bug0-0',
  1: 'bug4-0',
  2: 'bug1-0',
  3: 'ssb-q1',
  4: 'ssb-q11',
  5: 'bug4-1',
}

export class Problem {
  id

  /** @type {'qv' | 'qvm' | 'nm'} */
  method

  /** @type {Question} */
  question
  /** @type {Answer} */
  answer

  constructor(id, method, question) {
    this.id = id
    this.method = method
    this.question = question
  }

  instantiate() {
    const problem = new Problem(this.id, this.method, this.question)
    problem.answer = new Answer(problem.id, this.question.task, this.question.caseName, this.method)
    return problem
  }

  // backend URL
  getInstruction() {
    const task = this.question.task === 1 ? 'identify the issue' : 'locate the root cause'
    const caseName = this.question.caseName
    const caseId = ToCaseId[caseName]
    switch (this.method) {
      case 'qv':
        return `You are required to **${task}** using **our system**. Open [this link](${process.env.VUE_APP_FRONTEND_URL}/trace?case=${caseId}&method=qv) to visit the system webpage. <br/>The **transformation analysis support** is enabled.`
      case 'qvm':
        return `You are required to **${task}** using **our system**. Open [this link](${process.env.VUE_APP_FRONTEND_URL}/trace?case=${caseId}&method=qvm) to visit the system webpage. <br/>The **transformation analysis support** is DISABLED.`
      case 'nm':
        return `You are required to **${task}** using **log files**. Open VSCode ([online](http://10.16.71.4:8080/?folder=/home/zhengxin/qotrace/qotrace-web/Logs)) and open the log file \`Case${caseId}.txt\`.`
    }
  }
}
