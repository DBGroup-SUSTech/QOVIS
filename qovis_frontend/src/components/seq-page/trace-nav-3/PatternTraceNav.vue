<template>
  <div class="trace-nav">
    <svg :width="width" :height="height">
      <g v-if="traceTree" class="trace-root-group"
         :transform="`translate(${[traceTree.startX + treeMargin, traceTree.startY + treeMargin]})`">
        <g class="action-group">
          <PatternTraceNodeVis :trace-tree="traceTree"
                               :node-idx="0"
                               :trace-node="treeRoot"/>
        </g>
        <g class="plan-block-group">
          <rect v-for="(block, idx) in traceTree.planBlocks" :key="idx"
                class="plan-block"
                :x="block.centerX - block.width / 2"
                :y="block.topY"
                :width="block.width"
                :height="block.height"
                :fill="'#f0f0f0'"
                :stroke="'#606060'"
                stroke-width="1">
            <title>{{ `plan#${block.vPlanDag.plan.pid}` }}</title>
          </rect>
        </g>
        <g class="plan-dag-group">
          <PatternPlanView :trace-tree="traceTree"/>
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceTree2} from "@/js/seq2/PatternTraceTree"
import PatternTraceNodeVis from "@/components/seq-page/trace-nav-3/PatternTraceNodeVis"
import PatternPlanView from "@/components/seq-page/trace-nav-3/PatternPlanView"

export default {
  name: 'PatternTraceNav',
  components: {
    PatternPlanView,
    PatternTraceNodeVis
  },
  props: {
    traceTree: PatternTraceTree2,
  },
  data() {
    return {}
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {},
  computed: {
    ...mapState('seq2', {
      configV1: state => state.configV1,
      treeMargin: state => state.configV3.traceTree.margin,
    }),
    width() {
      return (this.traceTree?.width ?? 0) + this.treeMargin * 2
    },
    height() {
      return (this.traceTree?.height ?? 0) + this.treeMargin * 2
    },
    treeRoot() {
      return this.traceTree?.root ?? null
    },
  }
}
</script>

<style scoped>
.trace-nav {
  padding: 10px;
}
</style>
