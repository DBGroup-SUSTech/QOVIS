import Vue from 'vue'
import VueRouter from 'vue-router'
import TestPage from "@/view/TestPage"
import SummaryPage from "@/view/SummaryPage"
import NativePage from "@/view/NativePage"
import TimelinePage from "@/view/TimelinePage"
import SeqPage from "@/view/SeqPage"
import SeqPage2 from "@/view/SeqPage2"
import TracePage from "@/view/TracePage"
import ProbePage from "@/view/ProbePage"
import QuestionPage from "@/view/QuestionPage"

Vue.use(VueRouter)

const routes = [
  {path: '/timeline', component: TimelinePage},
  {path: '/summary', component: SummaryPage},
  {path: '/native', component: NativePage},
  {path: '/seq', component: SeqPage},
  {path: '/seq2', component: SeqPage2},
  {path: '/trace', component: TracePage},
  {path: '/probe', component: ProbePage},
  {path: '/test', component: TestPage},
  {path: '/question', component: QuestionPage},
  {path: '/', redirect: '/trace'},
]

export default new VueRouter({
  mode: 'history',
  routes
})
