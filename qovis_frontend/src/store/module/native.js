/* eslint-disable */
import {
  getDynamicGraph,
  getExampleList,
} from "@/service/module/dataService"
import {DynamicGraph} from "@/js/common/DynamicGraph"
import {OverviewTrace} from "@/js/native/TraceOverview"
import {PhaseGroup} from "@/js/native/PhaseGroup"
import {ConfigV1} from "@/js/config/ConfigV1"

// initial state
const state = () => ({
  configV1: new ConfigV1(),

  exampleList: [],
  exampleName: null,

  /** @type {DynamicGraph} */
  dynamicGraph: null,

  /** @type {OverviewTrace} */
  overviewTrace: null,
  /** @type {PhaseGroup[]} */
  phaseGroups: [],

  // interaction
  exampleChangeSign: true,
})

// getters
const getters = {}

// actions
const actions = {
  initExampleList({commit, dispatch}) {
    getExampleList(lst => {
      commit('changeExampleList', lst)
      dispatch('changeExample', lst[0])
    })
  },
  changeExample({commit}, exampleName) {
    console.log('Example change', exampleName)
    getDynamicGraph(exampleName, resp => {
      commit('changeDynamicGraph', resp)

      commit('computeOverviewTrace')
      commit('computePhaseGroups')

      commit('invokeExampleChangeSign')
    })
    commit('changeExampleName', exampleName)
  },
}

// mutations
const mutations = {
  changeExampleList(state, list) {
    state.exampleList = list
  },
  changeExampleName(state, exampleName) {
    state.exampleName = exampleName
  },
  invokeExampleChangeSign(state) {
    state.exampleChangeSign ^= true
  },
  changeDynamicGraph(state, dg) {
    state.dynamicGraph = DynamicGraph.load(dg)
    console.log(dg, state.dynamicGraph)
  },
  computeOverviewTrace(state) {
    state.overviewTrace = new OverviewTrace()
    state.overviewTrace.init(state.dynamicGraph.plans, state.dynamicGraph.phaseIntervals, state.dynamicGraph.phaseNames)
    state.overviewTrace.layout(state.configV1)

    console.log(state.overviewTrace)
  },
  computePhaseGroups(state) {
    state.phaseGroups = []
    const plans = state.dynamicGraph.plans
    const phaseIntervals = state.dynamicGraph.phaseIntervals
    const phaseNames = state.dynamicGraph.phaseNames
    console.log(state.dynamicGraph, phaseIntervals)
    for (let i = 0; i < phaseIntervals.length; i++) {
      const [start, end] = phaseIntervals[i]
      const planSlice = plans.slice(start, end)
      const phaseGroup = (new PhaseGroup()).init(phaseNames[i], planSlice)
      state.phaseGroups.push(phaseGroup)
      phaseGroup.layout(state.configV1)
    }
    console.log(state.phaseGroups)
  },
  changePhaseVisible(state, phaseIndex) {
    state.phaseGroups[phaseIndex].show ^= true
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
