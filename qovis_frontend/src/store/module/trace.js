/* eslint-disable */
import {
  getExampleList, getTraceData,
} from "@/service/module/dataService"
import {ConfigV3} from "@/js/config/ConfigV3"
import {Trace} from "@/js/trace/Trace"
import {VisTraceTree} from "@/js/trace/VisTraceTree"
import {getPosition} from "@/utils/Layout"
import gsap from 'gsap'

// initial state
const state = () => ({
  configV3: new ConfigV3(),

  exampleList: [],
  exampleName: null,

  scrollContainer: null,
  svgEl: null,

  /** @type {Trace} */
  trace: null,
  /** @type {VisTraceTree} */
  visTraceTree: null,

  // interaction
  exampleChangeSign: true,
  navigationChangeSignal: true,

  showEvoLabel: true,
  showUnchangeLink: false,
  /** @type {ParamItem | TransLink} */
  fixHighlightObject: null,

  transSupportEnabled: true,
  toEnlarge: false,
  hoverDelay: false,
})

// getters
const getters = {}

// actions
const actions = {
  initExampleList({state, commit, dispatch}, callback) {
    getExampleList(lst => {
      commit('changeExampleList', lst)
      if (callback) {
        callback()
      }
      if (state.exampleName === null) {
        dispatch('changeExample', lst[0])
      }
    })
  },
  changeExample({commit}, exampleName) {
    console.log('Example change', exampleName)
    getTraceData(exampleName, resp => {
      commit('changeTraceData', resp)
      commit('computeVisTraceTree')
      // commit('invokeExampleChangeSign')
    })
    commit('changeExampleName', exampleName)
  },
}

// mutations
const mutations = {
  mountScrollContainer(state, el) {
    state.scrollContainer = el
  },
  mountSvgEl(state, el) {
    state.svgEl = el
  },
  changeExampleList(state, list) {
    state.exampleList = list
  },
  changeExampleName(state, exampleName) {
    state.exampleName = exampleName
  },
  invokeExampleChangeSign(state) {
    state.exampleChangeSign ^= true
  },
  changeTraceData(state, trace) {
    console.log(trace)
    state.trace = new Trace().init({
      name: trace.name,
      plans: trace.plans,
      trans: trace.trans,
      tree: trace.tree,
      costs: trace.costs,
      linksMap: trace.linksMap,
    })
    console.log(state.trace)
  },
  computeVisTraceTree(state) {
    const traceTree = state.trace.traceTree
    state.visTraceTree = traceTree.createVisObj()
    state.visTraceTree.init(state.configV3)
    state.visTraceTree.initialLayout(state.configV3)
    // console.log(state.visTraceTree)
  },

  // interaction
  changeTransSupportState(state, enable) {
    state.transSupportEnabled = enable
  },
  /**
   * @param state
   * @param {VisTraceNode} node
   */
  toggleTraceNode(state, node) {
    // state.traceTree.initialLayout(state.configV2)
    state.visTraceTree.toggleTraceNode(state.configV3, node)
    if (state.fixHighlightObject !== null) {
      // reset the state
      state.fixHighlightObject.visObj.fixHighlight()
    }
    state.navigationChangeSignal ^= true
  },
  changeShowEvoLabel(state, show) {
    state.showEvoLabel = show
  },
  changeShowUnchangeLink(state, show) {
    if (!state.transSupportEnabled) {
      return
    }
    state.showUnchangeLink = show
  },
  changeToEnlarge(state, value) {
    state.toEnlarge = value
  },
  changeHoverDelay(state, delay) {
    state.hoverDelay = delay
  },
  /**
   * @param state
   * @param {VisParamItem | VisTransLink | null} visObj
   */
  changeFixHighlightObject(state, visObj) {
    if (!state.transSupportEnabled) {
      return
    }
    if (state.fixHighlightObject == null && visObj !== null) {
      state.fixHighlightObject = visObj.origin
      visObj.fixHighlight()
    } else if (state.fixHighlightObject !== null && visObj === null) {
      state.fixHighlightObject.visObj.unfixHighlight()
      state.fixHighlightObject = null
    } else if (state.fixHighlightObject !== null && visObj !== null) {
      if (state.fixHighlightObject.visObj === visObj) {
        // do nothing
      } else {
        state.fixHighlightObject.visObj.unfixHighlight()
        state.fixHighlightObject = visObj.origin
        visObj.fixHighlight()
      }
    } else {
      // state.fixHighlightItem === null && item === null
      // do nothing
    }
  },
  scrollToItemAndHighlight(state, {vItem, itemEl}) {
    if (!state.transSupportEnabled) {
      return
    }
    const targetX = getPosition(state.svgEl, itemEl).x + vItem.width / 2
    const targetLeft = targetX - state.scrollContainer.clientWidth / 2
    console.log(targetX, targetLeft)
    state.scrollContainer.scrollTo({
      left: targetLeft,
      behavior: 'smooth'
    })
    const {paramItemBaseColor, paramItemHighlightColor} = state.configV3.plan
    gsap.fromTo(vItem,
        {color: paramItemHighlightColor},
        {color: paramItemBaseColor, duration: 1.2})
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
