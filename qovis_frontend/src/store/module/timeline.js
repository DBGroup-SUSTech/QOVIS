/* eslint-disable */
import {
  getDynamicGraph,
  getExampleList, getSummaryData, getSummaryList,
} from "@/service/module/dataService"
import {SketchGraph} from "@/js/timeline/SketchGraph"
import {Plan} from "@/js/plan/Plan"

// initial state
const state = () => ({
  exampleList: [],
  exampleName: null,
  summaryList: [],
  summaryName: null,

  plans: [],
  summaryData: null,
  sketchGraph: null,

  /** @type {SketchGraphSimpleMeta} */
  sketchGraphSimpleMeta: null,
})

// getters
const getters = {}

// actions
const actions = {
  initExampleList({commit}) {
    getExampleList(lst => {
      commit('changeExampleList', lst)
      commit('changeExampleName', lst[1])
    })
  },
  changeExample({commit, dispatch}, exampleName) {
    getDynamicGraph(exampleName, resp => {
      commit('changePlans', resp.plans)

      getSummaryList(exampleName, resp => {
        commit('changeExampleName', exampleName)
        commit('changeSummaryList', resp)
        commit('changeSummaryName', "summary_7_r_tlc.json")
      })
    })
  },
  changeSummary({commit}, {exampleName, summaryName}) {
    getSummaryData(exampleName, summaryName, resp => {
      commit('changeSummaryData', {summaryName, data: resp})
    })
  }
}

// mutations
const mutations = {
  changeExampleList(state, list) {
    state.exampleList = list
  },
  changeExampleName(state, exampleName) {
    state.exampleName = exampleName
  },
  changePlans(state, plans) {
    state.plans = plans.map(p => Plan.load(p))
  },
  changeSummaryList(state, list) {
    state.summaryList = list
  },
  changeSummaryName(state, summaryName) {
    state.summaryName = summaryName
  },
  changeSummaryData(state, {summaryName, data}) {
    const toAlign = state.sketchGraphSimpleMeta?.toAlign

    state.summaryName = summaryName
    state.summaryData = data
    state.sketchGraph = SketchGraph.load(data.summary.sketch, state.plans)
    state.sketchGraphSimpleMeta = state.sketchGraph.createSimpleMeta(state.plans)
    state.sketchGraphSimpleMeta.toAlign = toAlign ?? false
    state.sketchGraphSimpleMeta.layout()
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
