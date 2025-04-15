<template>
  <div class="trace-plan-view">
    <svg v-for="(planDag, i) in this.traceTree.vPlanDags" :key="i"
         class="plan-item"
         :width="planDag.width" :height="planDag.height">
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

      <g :transform="'translate(' + [5, 5] + ')'">
        <!--      <rect fill="#fafafa" rx="3" ry="3"-->
        <!--            stroke="black" stroke-width="2"-->
        <!--            :width="plan.width" :height="plan.height"></rect>-->
        <g class="plan-group"
           @click="clickPlan(planDag, i)"
           :transform="'translate(' + [5, 5] + ')'">
          <g class="edge-group">
            <g v-for="(edge, i) in planDag.edges" :key="i">
              <path :d="edge.path" stroke-width="1" stroke="black" fill="none"/>
            </g>
          </g>
          <g class="node-group">
            <g v-for="(node, i) in planDag.nodes" :key="i" @click="clickNode(node)"
               :transform="'translate(' + [node.x, node.y] + ')'">
              <rect :fill="getEvoFill(node.getEvoType())" rx="3" ry="3"
                    stroke="black"
                    :width="node.width" :height="node.height">
                <title>{{ node.planNode.str }}</title>
              </rect>
              <text class="node-label" font-size="20"
                    :dx="node.width / 2" :dy="22"
                    text-anchor="middle">
                {{ getNodeLabel(node) }}
                <title>{{ node.planNode.str }}</title>
              </text>
            </g>
          </g>
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceTree} from "@/js/seq/PatternTraceTree"
import PatternTraceNodeVis from "@/components/seq-page/trace-nav-2/PatternTraceNodeVis"
import {getEvoTypeColor, getFadedColor} from "@/js/common"
import {VPlanDag} from "@/js/native/VPlanDag"

export default {
  name: 'PatternPlanView',
  components: {
    PatternTraceNodeVis
  },
  props: {
    traceTree: PatternTraceTree,
  },
  data() {
    return {
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    ...mapMutations('trace', [
        'changeVisGraphVisible'
    ]),
    clickSvg() {
      // console.log(this.visNode)
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
    getNodeLabel(vPlanNode) {
      if (!this.configV1.useOptAlias) {
        return vPlanNode.toLimitedString(this.configV1.plan.charLimit)
      }
      const alias = this.optInfoMap.get(vPlanNode.planNode.name)?.alias ?? '?'
      return vPlanNode.toAliasStr(alias)
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
      this.traceTree.computeVPlanDags(this.configV1)
    }
  },
  computed: {
    ...mapState('seq', {
      configV1: state => state.configV1,
      navigationChangeSignal: state => state.navigationChangeSignal,
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
</style>
