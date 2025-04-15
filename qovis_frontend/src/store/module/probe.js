/* eslint-disable */
import {ConfigV3} from "@/js/config/ConfigV3"
import {ProbeLine} from "@/js/probe/ProbeLine"
import {getProbeData, getProbeList} from "@/service/module/dataService"

// initial state
const state = () => ({
  configV3: new ConfigV3(),

  probeList: [],
  probeName: null,

  /** @type {ProbeLine[]} */
  probeLines: [],
  /** @type {VisProbeLine[]} */
  visProbeLines: [],

  // interaction
  probeChangeSign: true,

  showEvoLabel: true,
  showUnchangeLink: true,
})

// getters
const getters = {}

// actions
const actions = {
  initProbeList({commit, dispatch}) {
    getProbeList(lst => {
      commit('changeProbeList', lst)
      dispatch('changeProbe', lst[0])
    })
  },
  changeProbe({commit}, probeName) {
    console.log('Probe change', probeName)
    getProbeData(probeName, resp => {
      commit('changeProbeData', resp)
      commit('computeVisProbeLines')
      // commit('invokeExampleChangeSign')
    })
    commit('changeProbeName', probeName)
  },
}

// mutations
const mutations = {
  changeProbeList(state, list) {
    state.probeList = list
  },
  changeProbeName(state, probeName) {
    state.probeName = probeName
  },
  invokeProbeChangeSign(state) {
    state.invokeProbeChangeSign ^= true
  },
  changeProbeData(state, data) {
    const lines = data.split('\n')
        .filter(s => s.length > 0)
    const src = JSON.parse(lines[0])[2]
    const dst = JSON.parse(lines[1])[2]
    state.probeLines = lines
        .slice(2)
        .map(s => new ProbeLine().init(src, dst, JSON.parse(s)))
    console.log(data)
    console.log(state.probeLines)
  },
  computeVisProbeLines(state) {
    const lines = state.probeLines
    state.visProbeLines = lines.map(l => {
      const visLine = l.createVisObj()
      visLine.layout(state.configV3)
      return visLine
    })
  },

  // interaction
  changeShowEvoLabel(state, show) {
    state.showEvoLabel = show
  },
  changeShowUnchangeLink(state, show) {
    state.showUnchangeLink = show
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
