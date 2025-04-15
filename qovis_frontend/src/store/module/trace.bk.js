/* eslint-disable */
import {
  getDynamicGraph,
  getExampleList, getOptInfoList, getSummaryData, getSummaryList,
} from "@/service/module/dataService";
import {SGraph} from "@/js/summary/SummaryGraph"
import {MainSGraphMeta} from "@/js/main-view/MainSGraphMeta"
import {VisGraph} from "@/js/main-view/VisGraph"
import {TimelineOverviewMeta} from "@/js/common/TimelineOverviewMeta"
import {Plan} from "@/js/plan/Plan"
import {ConfigV1} from "@/js/config/ConfigV1"
import {OptInfo} from "@/js/common/OptInfo"

// initial state
const state = () => ({
  configV1: new ConfigV1(),

  exampleList: [],
  exampleName: null,
  summaryList: [],
  summaryName: null,

  optInfoMap: new Map(),

  plans: [],
  summaryData: null,
  /** @type {TimelineOverviewMeta} */
  toMeta: null,

  /** @type {SGraph[]} */
  sGraphs: [],
  /** @type {Object<int, boolean>[]} */
  effList: [],
  /** @type {Object<int, boolean>[]} */
  keyList: [],
  /** @type {VisGraph[]} */
  visGraphs: [],
  /** @type {MainSGraphMeta[]} */
  detailedSGraphMetas: [],

  renderOverviewDagSign: 0,
  renderMainDagSign: 0,

  // interaction
})

// getters
const getters = {}

// actions
const actions = {
  initExampleList({commit}) {
    getExampleList(lst => {
      commit('changeExampleList', lst)
      commit('changeExampleName', lst[0])
    })
    getOptInfoList(lst => {
      commit('changeOptInfoMap', lst)
    })
  },
  changeExample({commit, dispatch}, exampleName) {
    getDynamicGraph(exampleName, resp => {
      commit('changePlans', resp.plans)

      getSummaryList(exampleName, resp => {
        commit('changeExampleName', exampleName)
        commit('changeSummaryList', resp)
        commit('changeSummaryName', "summary_7_s_s.json")
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
  changeOptInfoMap(state, list) {
    state.optInfoMap = new Map()
    list.forEach(obj => {
      const optInfo = new OptInfo().init(obj)
      state.optInfoMap.set(optInfo.name, optInfo)
    })
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
    console.log('summary data', data)

    state.summaryName = summaryName
    state.summaryData = data
    state.sGraphs = data.summary.sgList.map(g => SGraph.load(g))
    state.effList = data.summary.effList
    state.keyList = data.summary.keyList

    state.toMeta = new TimelineOverviewMeta()
    state.toMeta.init(state.plans, data.summary.intervals, data.summary.impList)
    state.toMeta.layout(state.configV1)
    console.log(state.toMeta)

    state.detailedSGraphMetas = state.sGraphs.map(sg => new MainSGraphMeta(sg))

    state.visGraphs = data.summary.intervals.map(([start, end]) => {
      return new VisGraph(
          state.sGraphs.slice(start, end + 1),
          state.effList.slice(start, end + 1),
          []
      )
    })
    state.visGraphs.forEach(vg => vg.layout(state.configV1))

    console.log('sGraphs', state.sGraphs)
    console.log('visGraph', state.visGraphs)
  },
  changeVisGraphVisible(state, index) {
    state.visGraphs[index].show ^= true
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
