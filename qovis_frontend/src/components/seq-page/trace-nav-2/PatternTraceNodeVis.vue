<template>
  <g class="trace-node">
    <g v-if="isRoot">

    </g>
    <g v-else>
      <rect v-if="traceNode.expanded"
            class="trace-node-rect"
            :x="0"
            :y="0"
            :width="traceNode.expandedLayout.width"
            :height="traceNode.expandedLayout.height"
            fill="white"
            :stroke="'black'"
            rx="5"
            ry="5"
            stroke-width="2"></rect>
      <circle v-if="!traceNode.isPatternNode()"
              class="trace-node-circle"
              :cx="initialWidth / 2"
              :cy="initialHeight / 2"
              :r="circleRadius"
              :fill="getTraceNodeColor()"
              :stroke-width="traceNode.children.length !== 0 ? 2 : 0"
              :stroke="'gray'"
              @click="clickNode">
        <title>{{ `${traceNode.plans.length} plan(s)` }}</title>
      </circle>
      <rect v-else
            class="trace-node-circle"
            :x="initialWidth / 2 - circleRadius"
            :y="initialHeight / 2 - circleRadius"
            :width="circleRadius * 2"
            :height="circleRadius * 2"
            :fill="getTraceNodeColor()"
            :stroke-width="traceNode.children.length !== 0 ? 2 : 0"
            :stroke="'gray'"
            @click="clickNode">
        <title>{{ `${traceNode.getSimpleNameWithCnt()}\n` }}
          {{ `${traceNode.plans.length} action(s)\n` }}
          {{ `${getVisTimeCost(traceNode.getTimeCost())}` }}</title>
      </rect>
      <text class="circle-text"
            text-anchor="middle"
            :transform="`translate(${[initialWidth/2, initialHeight/2+5]})`">{{ traceNode.plans.length }}</text>
<!--      <text v-if="traceNode.isPatternNode() && (traceNode.desc === '*' || traceNode.desc === '+') && traceNode.children.length > 1"-->
<!--            class="circle-text"-->
<!--            text-anchor="start"-->
<!--            font-size="14"-->
<!--            :transform="`translate(${[initialWidth/2 + circleRadius + 2, initialHeight/2-circleRadius + 8]})`">{{ traceNode.children.length }}</text>-->
          <text v-if="showTimeCost"
                class="circle-text"
                text-anchor="start"
                font-size="12"
                :transform="`translate(${[initialWidth/2 + circleRadius + 2, 15]})`">{{ getVisTimeCost(traceNode.getTimeCost()) }}</text>
      <text class="trace-node-text"
            text-anchor="start"
            :transform="textTransform">{{ traceNode.getSimpleNameWithCnt() }}</text>
    </g>
    <g v-if="traceNode.expanded" class="children-group">
      <g v-for="(pair, idx) in childPairs"
         :key="'line' + idx"
         :transform="`translate(${[initialWidth / 2, initialHeight /2]})`">
        <line class="trace-node-line"
              :x1="pair[0].x"
              :y1="pair[0].y"
              :x2="pair[1].x"
              :y2="pair[1].y"
              :stroke="'#949494'"
              stroke-width="4"></line>
      </g>
      <PatternTraceNodeVis v-for="(child, idx) in traceNode.children"
                    :key="idx"
                    :trace-tree="traceTree"
                    :trace-node="child"
                    :node-idx="idx"
                    :transform="`translate(${[child.x, child.y]})`"/>
    </g>
  </g>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {PatternTraceNode, PatternTraceTree} from "@/js/seq/PatternTraceTree"

export default {
  name: 'PatternTraceNodeVis',
  components: {
  },
  props: {
    traceTree: PatternTraceTree,
    nodeIdx: Number,
    traceNode: PatternTraceNode,
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  methods: {
    ...mapMutations('seq', [
      'toggleTraceNode',
    ]),
    clickNode() {
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
    ...mapState('seq', {
      configV2: state => state.configV2,
      initialWidth: state => state.configV2.traceNode.initialWidth,
      initialHeight: state => state.configV2.traceNode.initialHeight,
      textOffsetX: state => state.configV2.traceNode.textOffsetX,
      textOffsetY: state => state.configV2.traceNode.textOffsetY,
      textRotation: state => state.configV2.traceNode.textRotation,
      fontSize: state => state.configV2.traceNode.fontSize,
      showTimeCost: state => state.showTimeCost,
    }),
    textTransform() {
      if (this.traceNode.expanded) {
        return `translate(${this.initialWidth}, ${this.initialHeight / 2 + 10/2})`
      } else {
        return `translate(${this.initialWidth / 2 + this.textOffsetX}, ${this.initialHeight + this.textOffsetY}) rotate(${this.textRotation})`
      }
    },
    circleRadius() {
      return this.traceTree.sizeScale(this.traceNode.plans.length / this.traceTree.root.plans.length)
    },
    isRoot() {
      return this.traceNode.isRoot
    },
    childPairs() {
      const pairs = []
      for (let i = 0; i < this.traceNode.children.length - 1; i++) {
        pairs.push([this.traceNode.children[i], this.traceNode.children[i + 1]])
      }
      return pairs
    }
  }
}
</script>

<style scoped>
.trace-node {
}
.circle-text {
  cursor: pointer;
  user-select: none;
  pointer-events: none;
}
.trace-node-circle {
  cursor: pointer;
}
.trace-node-text {
  user-select: none;
}
</style>
