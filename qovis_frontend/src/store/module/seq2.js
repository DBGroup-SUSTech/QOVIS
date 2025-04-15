/* eslint-disable */
import {
  getDynamicGraph,
  getExampleList,
} from "@/service/module/dataService"
import {DynamicGraph} from "@/js/common/DynamicGraph"
import {ConfigV2} from "@/js/config/ConfigV2"
import {Patterns} from "@/assets/patterns"
import {Pattern, PatternItem} from "@/js/seq/Pattern"
import {ConfigV1} from "@/js/config/ConfigV1"
import {PatternTraceTree2} from "@/js/seq2/PatternTraceTree"
import {ConfigV3} from "@/js/config/ConfigV3"

function getPatterns() {
  return Patterns.map(raw => {
    const p = new Pattern()
    p.name = raw.name
    p.type = raw.type
    if ('items' in raw) {
      p.items = raw.items.map(item => {
        const i = new PatternItem()
        i.name = item.name
        i.desc = item.desc
        return i
      })
    }
    return p
  })
}

// initial state
const state = () => ({
  configV1: new ConfigV1(),
  configV2: new ConfigV2(),
  configV3: new ConfigV3(),

  exampleList: [],
  exampleName: null,

  /** @type {DynamicGraph} */
  dynamicGraph: null,
  /** @type {PatternTraceTree2} */
  patternTraceTree: null,
  /** @type {Pattern[]} */
  patterns: getPatterns(),

  // interaction
  exampleChangeSign: true,
  navigationChangeSignal: true,

  showTimeCost: true,
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

      commit('computeTraceTree')

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
  changePatterns(state, patterns) {
    state.patterns = patterns
  },
  changeShowTimeCost(state, showTimeCost) {
    state.showTimeCost = showTimeCost
  },
  computeTraceTree(state) {
    state.patternTraceTree = new PatternTraceTree2(state.configV3, state.dynamicGraph, state.patterns)
    state.patternTraceTree.initialLayout(state.configV3)
    console.log(state.patternTraceTree)
    state.navigationChangeSignal ^= true
  },

  // interaction
  /**
   * @param state
   * @param {PatternTraceNode2} node
   */
  toggleTraceNode(state, node) {
    // state.traceTree.initialLayout(state.configV2)
    state.patternTraceTree.toggleTraceNode(state.configV3, node)
    state.navigationChangeSignal ^= true
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
