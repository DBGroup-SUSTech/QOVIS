<template>
  <div class="trace-nav">
    <svg :width="width" :height="height">
      <PatternTraceNodeVis v-if="treeRoot"
                    :trace-tree="traceTree"
                    :node-idx="0"
                    :trace-node="treeRoot"
                    :transform="`translate(${[treeRoot.x, treeRoot.y]})`"/>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceTree} from "@/js/seq/PatternTraceTree"
import PatternTraceNodeVis from "@/components/seq-page/trace-nav-2/PatternTraceNodeVis"

export default {
  name: 'PatternTraceNav',
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
    clickPhase(phase) {
      console.log(phase)
      this.changeVisGraphVisible(phase.phaseIndex)
    },
    getBorderWidth(phase) {
      return (this.visGraphs[phase.phaseIndex].show ? 2 : 1) * phase.borderWidth
    },
    getStroke(phase) {
      return this.visGraphs[phase.phaseIndex].show ? '#699bef' : 'gray'
    },
    getAlias(name) {
      return name.includes('JoinSelection') ? 'JoinSelection' : name
    }
  },
  computed: {
    ...mapState('trace', {
      configV1: state => state.configV1,
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
.trace-nav {
  padding: 10px;
}
</style>
