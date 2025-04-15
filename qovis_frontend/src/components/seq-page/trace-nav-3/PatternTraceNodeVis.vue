<template>
  <g class="trace-node">
    <g v-if="isRoot">

    </g>
    <g v-else
       :transform="`translate(${[traceNode.x, traceNode.y]})`">
      <rect v-if="!traceNode.isPatternNode()"
            class="trace-node-rect"
            :width="traceNode.width"
            :height="traceNode.height"
            :fill="getTraceNodeColor()"
            @click="clickNode">
        <title>{{ `${traceNode.getSimpleNameWithCnt()}\n` }}
          {{ `${traceNode.getPlans().length} action(s)\n` }}
          {{ `${getVisTimeCost(traceNode.getTimeCost())}` }}</title>
      </rect>
      <rect v-else
            class="trace-node-rect"
            :width="traceNode.width"
            :height="traceNode.height"
            :fill="getTraceNodeColor()"
            @click="clickNode">
        <title>{{ `${traceNode.getSimpleName()}\n` }}
          {{ `${traceNode.getPlans().length} action(s)\n` }}
          {{ `${getVisTimeCost(traceNode.getTimeCost())}` }}</title>
      </rect>
      <text class="trace-node-text"
            :dx="traceNode.width / 2"
            :dy="rowHeight - fontSize / 3"
            :font-size="fontSize"
            text-anchor="middle">{{ getTraceNodeText() }}</text>
    </g>
    <g v-if="traceNode.expanded" class="children-group">
      <PatternTraceNodeVis v-for="(child, idx) in traceNode.children"
                           :key="idx"
                           :trace-tree="traceTree"
                           :trace-node="child"
                           :node-idx="idx"/>
    </g>
  </g>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceNode2, PatternTraceTree2} from "@/js/seq2/PatternTraceTree"
import {getLimitedString} from "@/utils/Layout"

export default {
  name: 'PatternTraceNodeVis',
  components: {},
  props: {
    traceTree: PatternTraceTree2,
    nodeIdx: Number,
    traceNode: PatternTraceNode2,
  },
  data() {
    return {}
  },
  mounted() {
  },
  methods: {
    ...mapMutations('seq2', [
      'toggleTraceNode',
    ]),
    getTraceNodeText() {
      let str = this.traceNode.getSimpleName()
      str = getLimitedString(str, this.traceNode.width * 0.8, this.fontSize)
      if (this.traceNode.isPatternNode() && this.traceNode.children.length > 1) {
        str += ` (${this.traceNode.children.length})`
      }
      return str
    },
    clickNode() {
      console.log(this.traceNode, this.traceTree.getVPlanDag(this.traceNode.startIdx), this.traceTree.getVPlanDag(this.traceNode.endIdx))
      if (this.traceNode.children.length === 0) {
        return
      }
      console.log(this.traceNode)
      this.toggleTraceNode(this.traceNode)
    },
    getTraceNodeColor() {
      return this.traceTree.getColor(this.traceNode)
    },
    getVisTimeCost(timeCost) {
      // timeCost is in ns
      if (timeCost < 1000) {
        return `${timeCost} ns`
      } else if (timeCost < 1000000) {
        return `${(timeCost / 1000).toFixed(2)} us`
      } else if (timeCost < 1000000000) {
        return `${(timeCost / 1000000).toFixed(2)} ms`
      } else {
        return `${(timeCost / 1000000000).toFixed(2)} s`
      }
    }
  },
  computed: {
    ...mapState('seq2', {
      configV2: state => state.configV3,
      rowHeight: state => state.configV3.nav.rowHeight,
      fontSize: state => state.configV3.nav.fontSize,
    }),
    isRoot() {
      return this.traceNode.isRoot
    },
  }
}
</script>

<style scoped>
.trace-node {
}

.trace-node-rect {
  cursor: pointer;
  opacity: 0.7;
}

.trace-node-text {
  cursor: pointer;
  user-select: none;
  pointer-events: none;
}
</style>
