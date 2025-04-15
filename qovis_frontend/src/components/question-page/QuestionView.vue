<template>
  <div class="question-component">
    <div class="step-container">
      <el-steps :active="currentStep" finish-status="success" simple v-show="!devMode">
        <el-step title="Start"></el-step>
        <el-step title="Tutorial"></el-step>
        <el-step v-for="(title, idx) in problemTitles" :key="idx" :title="title"></el-step>
        <el-step title="Finish!"></el-step>
      </el-steps>
      <span v-show="devMode" class="dev" >
        <el-button type="primary" @click="currentStep = 0" style="margin: 20px;">Hello page</el-button>
        <el-button type="primary" @click="currentStep = 1" style="margin: 20px;">Tutorial page</el-button>
        <el-select v-model="devProblemIdx" style="margin-top: 20px;" @change="devSelectChange">
          <el-option v-for="(p, idx) in problems" :key="idx" :label="p.id" :value="idx"></el-option>
        </el-select>
        <el-button type="primary" @click="goToLastPage" style="margin: 20px;">Last page</el-button>
        <el-button type="primary" @click="problemScreenshot" style="margin: 20px;">Screenshot</el-button>
        <el-button type="primary" @click="problemScreenshotAll" style="margin: 20px;">Screenshot all</el-button>
      </span>
    </div>

    <div class="question-body">
      <div v-show="currentStep === 0" class="step-page">
        <h2>Thanks for participating in our user study!</h2>
        <p>Please fill in the following information.</p>
        <div style="width: 800px;">
          <el-form ref="form" :model="form" label-width="140px">
            <el-form-item label="Name">
              <el-input v-model="form.name" placeholder="Your full name"></el-input>
            </el-form-item>
            <el-form-item label="Gender">
              <el-radio-group v-model="form.gender">
                <el-radio label="Male"></el-radio>
                <el-radio label="Female"></el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Age">
              <el-input v-model="form.age" placeholder="Your age"></el-input>
            </el-form-item>
            <el-form-item label="Email">
              <el-input v-model="form.email" placeholder="Your email"></el-input>
            </el-form-item>
            <el-form-item label="You are">
              <el-radio-group v-model="form.level">
                <el-radio label="Undergraduate"></el-radio>
                <el-radio label="Master"></el-radio>
                <el-radio label="Ph.D."></el-radio>
                <el-radio label="Professor"></el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Major">
              <el-input v-model="form.major" placeholder="Your major (your research direction)" type="textarea"></el-input>
            </el-form-item>
            <el-form-item label="Familiar with">
              <el-checkbox-group v-model="form.familiarWith">
                <el-checkbox label="Visualization" name="type"></el-checkbox>
                <el-checkbox label="Database" name="type"></el-checkbox>
                <el-checkbox label="Query Optimization" name="type"></el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit">Next</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <div v-show="currentStep === 1"  class="step-page">
        <h1>Tutorial</h1>
<!--        <p><em>QOVIS</em> is a visual analysis system designed for the query optimization in DBMS.</p>-->
<!--        <el-divider/>-->
        <p>Click <a href="resources/Tutorial.pptx" target="_blank">here</a> download the tutorial PPT, which introduces the background and the usage of the system.</p>
        <el-divider/>
        <p>
          Before starting the user study, ensure that you can view the log files online at <a href="http://10.16.71.4:8080/?folder=/home/zhengxin/qotrace/qotrace-web/Logs" target="_blank">this webpage</a> with password <em></em>.
          Or you can <a href="resources/Logs.zip" target="_blank">download the log files</a>. (VSCode is recommended for viewing the log files).
        </p>
        <p>You can visit and get familiar with <a :href="getExampleURL()" target="_blank">our visual analysis system</a>.</p>
        <el-divider/>
        <el-button type="primary" @click="nextStep">Start the user study</el-button>
      </div>
      <div v-for="(problem, pIdx) in problems" :key="problem.id"
           v-show="pIdx + 2 === currentStep"
           class="step-page">
        <h1 v-if="!devMode">{{fullProblemTitles[pIdx]}}</h1>
        <h1 v-else>{{getDevProblemTitle(pIdx)}}</h1>
        <div ref="markdownField"
             style="display: flex; flex-direction: column; align-items: flex-start">
          <div v-html="parseMarkdown(problem.question.description)"></div>
          <el-divider/>
          <div v-html="parseMarkdown(problem.getInstruction())"></div>

          <el-divider/>

          <div v-html="parseMarkdown(problem.question.head)"></div>
          <el-radio-group v-model="currentSelection"
                          style="display: flex; flex-direction: column; align-items: flex-start">
            <el-radio v-for="option in problem.question.options" :key="option.id" :label="option.id"><span v-html="parseOptionMarkdown(option.text)"/></el-radio>
          </el-radio-group>

          <el-divider/>

          <div style="display: flex; justify-content: flex-start; align-items: center; font-size: 20px;">
            <span style="margin-top: 10px;">What is your reason?</span>
            <el-input v-model="reasonStr" style="width: 440px; margin-left: 20px; margin-top: 10px;" type="textarea"></el-input>
          </div>
          <div style="display: flex; justify-content: flex-start; align-items: center; font-size: 20px;">
            <span style="margin-top: 10px;">How confident are you with your answer?</span>
            <div style="display: flex; justify-content: flex-start; width: 440px; padding-left: 20px;">
              <el-rate
                  v-model="confident"
                  :icon-classes="iconClasses"
                  void-icon-class="icon-rate-face-off"
                  show-text
                  :texts="confidentTexts"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']">
              </el-rate>
            </div>
          </div>
          <el-button type="primary" @click="checkSelection"
                     style="margin-top: 20px;"
                     :disabled="currentSelection === null || confident === null || reasonStr === ''">Check</el-button>
          <el-button v-show="devMode" class="dev"
                     type="primary" @click="checkSelection"
                     style="margin-top: 20px;">Check (Dev)</el-button>
        </div>

      </div>
      <div v-show="currentStep >= this.problems.length + 2"  class="step-page" style="text-align: center;">
        <h1>Thank you for your participation!</h1>
        <el-divider/>
        <p v-if="submitted">Your result has been submitted.</p>
        <p v-else>Click the buttons below to submit and download your result.</p>
        <span>
          <el-button type="primary" @click="submitResult"
                             style="margin-right: 30px;">Submit result</el-button>
          <el-button type="primary" @click="download">Download result</el-button>
        </span>
        <el-divider/>
        <p>Please click <a href="https://wj.qq.com/s2/14343076/2fcb/" target="_blank">here</a> to fill in the post-study questionnaire.</p>
      </div>
    </div>

    <el-dialog
        title="Correct answer!"
        :visible.sync="correctDialogVisible"
        width="300px"
        center>
      <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <el-button type="primary" plain @click="correctDialogVisible = false; nextStep()">Next question</el-button>
      </div>
    </el-dialog>
    <el-dialog
        title="Wrong answer!"
        :visible.sync="wrongDialogVisible"
        width="300px"
        center>
      <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <el-button type="danger" plain @click="wrongDialogVisible = false;">Try again</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import {mapMutations, mapState} from 'vuex';
import {Person} from "@/js/question/People"
import {Converter} from "showdown"
import {problemGen} from "@/js/question/ProblemGen"
import domtoimage from 'dom-to-image'
import {saveAs} from 'file-saver'
import {changeTitle} from "@/utils/Title"

// http://localhost:14000/question?pid=0&order=0

export default {
  name: 'QuestionView',
  data() {
    return {
      converter: new Converter(),
      currentStep: 0,   // 0: start, 1: tutorial, 2~: questions, n+2: finish. n = questionData.length = 8
      devMode: false,
      devProblemIdx: 0,

      pid: null,
      order: null,
      form: {
        name: '',
        gender: '',
        age: null,
        email: '',
        level: '',
        major: '',
        familiarWith: [],
      },

      currentSelection: null,     // option.id
      confident: null,            // 1-5
      reasonStr: '',

      problemTitles: [
        'T1Q1', 'T1Q2', 'T1Q3', 'T1Q4', 'T1Q5', 'T1Q6',
        'T2Q1', 'T2Q2', 'T2Q3'
      ],
      fullProblemTitles: [
        'Task 1 Question 1', 'Task 1 Question 2', 'Task 1 Question 3', 'Task 1 Question 4', 'Task 1 Question 5', 'Task 1 Question 6',
        'Task 2 Question 1', 'Task 2 Question 2', 'Task 2 Question 3'
      ],
      iconClasses: ['icon-rate-face-1', 'icon-rate-face-2', 'icon-rate-face-3'],
      // 5 level, where 3 is the middle
      confidentTexts: [
          "Not confident",
          "Slightly confident",
          "Confident",
          "Very confident",
          "Extremely confident",
      ],

      person: null,
      /** @type{Problem[]} */
      problems: [],

      checkDialogVisible: false,
      correctDialogVisible: false,
      wrongDialogVisible: false,
    }
  },
  mounted() {
    changeTitle('User Study')

    this.changeSubmitted(false)
    try {
      this.pid = parseInt(this.$route.query.pid)
      this.order = parseInt(this.$route.query.order)
      if (isNaN(this.pid) || isNaN(this.order)) {
        throw new Error('Invalid parameters')
      }
    } catch (e) {
      console.log(e)
      // notice
      this.$notify.error({
        title: 'Error',
        message: 'Invalid parameters. Please check the URL. Required parameters: pid, order.'
      })
    }
    this.devMode = this.$route.query.dev !== undefined
    if (this.devMode) {
      this.createProblemsDev()
    } else {
      this.createProblems()
    }
  },
  methods: {
    ...mapMutations('question', {
      changeSubmitted: state => state.changeSubmitted,
    }),
    getExampleURL() {
      return process.env.VUE_APP_FRONTEND_URL + '/trace?example'
    },
    getCurrentProblem() {
      const id = this.currentStep - 2
      if (id < 0 || id >= this.problems.length) {
        return null
      }
      return this.problems[id]
    },
    nextStep() {
      this.currentStep += 1
      this.currentSelection = null
      this.confident = null
      this.reasonStr = ''

      const problem = this.getCurrentProblem()
      if (problem != null) {
        problem.answer.startAnswer()
      }
    },
    onSubmit() {
      const person = new Person()
      person.pid = this.pid
      person.order = this.order
      person.name = this.form.name
      person.gender = this.form.gender
      person.age = parseInt(this.form.age)
      person.email = this.form.email
      person.level = this.form.level
      person.major = this.form.major
      person.familiarWithVIS = this.form.familiarWith.includes('Visualization')
      person.familiarWithDB = this.form.familiarWith.includes('Database')
      person.familiarWithQO = this.form.familiarWith.includes('Query Optimization')
      this.person = person

      console.log(this.person)

      this.nextStep()
    },
    createProblems() {
      this.problems = problemGen.getProblems(this.order)
    },
    createProblemsDev() {
      this.problems = problemGen.getProblemsDev()
    },
    checkSelection() {
      const problem = this.getCurrentProblem()
      if (problem == null) {
        console.error('No question found')
      }
      problem.answer.addAnswer(this.currentSelection, this.confident, this.reasonStr)
      if (problem.question.correctOptionId === this.currentSelection) {
        problem.answer.endAnswer()
        this.correctDialogVisible = true
      } else {
        this.confident = null
        this.reasonStr = ''
        this.wrongDialogVisible = true
      }
    },
    getResult() {
      return {
        person: this.person,
        answers: this.problems.map(p => p.answer.toJson())
      }
    },
    submitResult() {
      this.$store.dispatch('question/postResult', {
        result: this.getResult(),
        vueComponent: this,
      })
    },
    download() {
      const result = this.getResult()
      const data = JSON.stringify(result, null, 2)
      const blob = new Blob([data], {type: 'text/plain'})
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${this.person.pid} ${this.person.name}.json`
      a.click()
      window.URL.revokeObjectURL(url)
    },
    parseMarkdown(text) {
      const htmlStr = this.converter.makeHtml(text)
      // parse, modify <a> and convert back to str
      const parser = new DOMParser()
      const doc = parser.parseFromString(htmlStr, 'text/html')
      doc.querySelectorAll('a').forEach(function (link) {
        link.setAttribute('target', '_blank')
      })
      // center images
      doc.querySelectorAll('img').forEach(function (img) {
        img.style.display = 'block'
        img.style.margin = 'auto'
      })
      return new XMLSerializer().serializeToString(doc)
    },
    parseOptionMarkdown(text) {
      const htmlStr = this.converter.makeHtml(text)
      const parser = new DOMParser()
      const doc = parser.parseFromString(htmlStr, 'text/html')
      // change first p to span
      doc.querySelector('p').outerHTML = `<span>${doc.querySelector('p').innerHTML}</span>`
      return new XMLSerializer().serializeToString(doc)
    },
    devSelectChange() {
      this.currentStep = this.devProblemIdx + 2
    },
    goToLastPage() {
      this.currentStep = this.problems.length + 2
    },
    getDevProblemTitle(pIdx) {
      const problem = this.problems[pIdx]
      const question = problem.question
      return `Problem ${problem.id} (Task ${question.task}, Case ${question.caseName}, Method ${problem.method})`
    },
    problemScreenshotAll() {
      this.currentStep = 0
      const recursive = async () => {
        if (this.currentStep < this.problems.length + 3) {
          await this.problemScreenshot()
          this.nextStep()
          // wait 1s for next step
          await new Promise((resolve) => setTimeout(resolve, 1000))
          return recursive()
        }
      }
      recursive()
    },
    async problemScreenshot() {
      const dom = document.querySelector('.question-body').cloneNode(true)
      if (dom == null) {
        console.error('No visible step-page found')
        this.$message.error('No visible step-page found')
        return new Promise((resolve, reject) => reject('No visible step-page found'))
      }
      // reset height and overflow
      dom.style.height = 'auto'
      dom.style.overflow = 'visible'
      // remove all element with class "dev"
      dom.querySelectorAll('.dev').forEach(e => e.remove())

      // insert into .question-component
      const parent = document.querySelector('.question-component')
      parent.appendChild(dom)
      // wait for dom to be added
      await new Promise((resolve) => setTimeout(resolve, 100))
      const blob = await domtoimage.toPng(dom, {})
      const filename = `Step${this.currentStep}.png`
      await saveAs(blob, filename)
      // remove dom
      parent.removeChild(dom)
    }
  },
  computed: {
    ...mapState('question', {
      questions: state => state.questions,
      submitted: state => state.submitted,
    }),
  }
}
</script>

<style scoped>
.step-container {
  width: 100%;
}

.question-component >>> .el-dialog__title {
  font-size: 25px;
  font-weight: 500;
}

.question-component >>> .el-button {
  font-size: 15px;
  font-weight: 500;
}

.question-component >>> .el-rate__text {
  font-size: 20px;
  font-weight: 500;
  margin-left: 15px;
}

.question-component >>> .el-rate__icon {
  font-size: 30px;
}

.question-component {
  width: 100%;
  height: 100%;
}
.question-body {
  height: calc(100% - 146px);
  padding: 50px 200px;
  overflow: scroll;
  background: white;
}
.step-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
}
.step-page >>> p, .step-page >>> span, .step-page >>> label {
  font-size: 20px;
  font-weight: 500;
  text-align: left;
}
</style>
