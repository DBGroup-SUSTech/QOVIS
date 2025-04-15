<template>
  <g class="trace-plan-view">
    <defs>
      <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>
      </linearGradient>
      <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
      </linearGradient>
      <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
      </linearGradient>
      <!--      <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--      </linearGradient>-->
      <!--      <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--      </linearGradient>-->
      <!--      <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--      </linearGradient>-->
    </defs>
    <g v-for="(block, i) in this.traceTree.planBlocks" :key="i"
         class="plan-item"
         :transform="`translate(${[block.vPlanDag.x, block.vPlanDag.y]})`">
<!--      <rect fill="#fafafa" rx="3" ry="3"-->
<!--            stroke="black" stroke-width="2"-->
<!--            :width="block.vPlanDag.width" :height="block.vPlanDag.height"></rect>-->
      <g class="plan-group"
         @click="clickPlan(block.vPlanDag, i)"
         :transform="'translate(' + [planPadding, planPadding] + ')'">
        <g class="edge-group">
          <g v-for="(edge, i) in block.vPlanDag.edges" :key="i">
            <path :d="edge.path" stroke-width="1" stroke="black" fill="none"/>
          </g>
        </g>
        <g class="node-group">
          <g v-for="(node, i) in block.vPlanDag.nodes" :key="i" @click="clickNode(node)"
             :transform="'translate(' + [node.x, node.y] + ')'">
            <rect :fill="getEvoFill('U')" rx="3" ry="3"
                  stroke="black"
                  :width="node.width" :height="node.height">
              <title>{{ node.planNode.str }}</title>
            </rect>
            <text class="node-label"
                  :font-size="fontSize"
                  :dx="node.width / 2" :dy="node.height - fontSize / 3"
                  text-anchor="middle">
              <tspan>{{ getNodeName(node) }}</tspan>
              <tspan :dy="-fontSize * 0.3" :font-size="fontSize * idScale">#{{ getNodeId(node) }}</tspan>
              <title>{{ node.planNode.str }}</title>
            </text>
            <g class="icon-group">
              <g v-if="node.isAdded()"
                 :transform="`translate(${[-iconSize/2, (node.height - iconSize)/2]})`">
                <svg t="1687245465763" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9614" :width="iconSize" :height="iconSize">
                  <circle :cx="1024 / 2" :cy="1024 / 2" :r="1024 * 0.3" fill="white"/>
                  <path :fill="'#5dbb54'" d="M512 64C213.3 64 64 213.3 64 512s149.3 448 448 448 448-149.3 448-448S810.7 64 512 64z m224.2 513.3H577.7v158.5c0 31.8-25.8 57.6-57.6 57.6s-57.6-25.8-57.6-57.6V577.3H303.9c-31.8 0-57.6-25.8-57.6-57.7 0-31.8 25.8-57.6 57.6-57.6h158.5V303.5c0-31.9 25.8-57.6 57.6-57.6s57.6 25.7 57.6 57.6V462h158.5c31.8 0 57.6 25.8 57.6 57.6 0.2 31.9-25.6 57.7-57.5 57.7z" p-id="9615"></path></svg>
              </g>
              <g v-if="node.toRemove()"
                 :transform="`translate(${[node.width - iconSize/2, (node.height - iconSize)/2]})`">
                <svg t="1687245508476" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9759" :width="iconSize" :height="iconSize">
                  <circle :cx="1024 / 2" :cy="1024 / 2" :r="1024 * 0.3" fill="white"/>
                  <path :fill="'#ff5454'" d="M512 64C213.3 64 64 213.3 64 512s149.3 448 448 448 448-149.3 448-448S810.7 64 512 64z m224.2 513.3H303.9c-31.8 0-57.6-25.8-57.6-57.7 0-31.8 25.8-57.6 57.6-57.6h432.4c31.8 0 57.6 25.8 57.6 57.6 0 31.9-25.8 57.7-57.7 57.7z" p-id="9760"></path></svg>
              </g>
            </g>
          </g>
        </g>
      </g>
    </g>
  </g>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceTree2} from "@/js/seq2/PatternTraceTree"
import {getEvoTypeColor, getFadedColor} from "@/js/common"
import {getLimitedString, getTextSize} from "@/utils/Layout"

export default {
  name: 'PatternPlanView',
  components: {
  },
  props: {
    traceTree: PatternTraceTree2,
  },
  data() {
    return {
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    ...mapMutations('seq2', []),
    clickSvg() {
    },
    clickAction(act) {
      console.log(act)
    },
    clickPlan(planDag, i) {
      console.log(planDag.plan)
      for (const info of planDag.plan.infoList) {
        console.log(info, JSON.stringify(Object.assign(info, {plan: 'hidden'})))
      }
      if (planDag.plan.infoList.length === 0) {
        console.log("Empty info list")
      }
    },
    clickNode(node) {
      console.log(node.toString())
      console.log(node.planNode.str)
      console.log(node)
    },
    getNodeName(vPlanNode) {
      const {useOptAlias} = this.configV3
      const {nodeWidth, fontSize, idScale} = this.configV3.plan

      const id = vPlanNode.getNodeId()
      const {width: idWidth} = getTextSize('#' + id, fontSize * idScale)

      let name = vPlanNode.getNodeName()
      if (useOptAlias) {
        name = this.optInfoMap.get(vPlanNode.planNode.name)?.alias ?? '?'
      }
      name = getLimitedString(name, nodeWidth - idWidth, fontSize)

      return name
    },
    getNodeId(vPlanNode) {
      return vPlanNode.getNodeId()
    },
    getEvoFill(type) {
      switch (type) {
        case 'A': return 'url(#gradient-add)'
        case 'R': return 'url(#gradient-remove)'
        case 'AR': return 'url(#gradient-add-remove)'
        case 'U': return getEvoTypeColor('U')
      }
      return 'red'
    },
    getEvoTypeColor(type) {
      return getEvoTypeColor(type)
    },
    getMetaTypeColor(type) {
      return getFadedColor(type)
    }
  },
  watch: {
    navigationChangeSignal() {
    }
  },
  computed: {
    ...mapState('seq2', {
      configV1: state => state.configV1,
      navigationChangeSignal: state => state.navigationChangeSignal,
      configV3: state => state.configV3,
      planPadding: state => state.configV3.plan.padding,
      fontSize: state => state.configV3.plan.fontSize,
      idScale: state => state.configV3.plan.idScale,
      iconSize: state => state.configV3.plan.iconSize,
    }),
    width() {
      return this.traceTree?.width ?? 0
    },
    height() {
      return this.traceTree?.height ?? 0
    },
    treeRoot() {
      return this.traceTree?.root ?? null
    },
  }
}
</script>

<style scoped>
.trace-plan-view {
  padding: 10px;

  display: flex;
  overflow: auto;
}
.plan-item {
  flex-shrink: 0;
}
.node-label {
  user-select: none;
}
</style>
