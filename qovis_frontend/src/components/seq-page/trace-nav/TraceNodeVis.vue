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
      <circle class="trace-node-circle"
              :cx="initialWidth / 2"
              :cy="initialHeight / 2"
              :r="circleRadius"
              :fill="getTraceNodeColor()"
              :stroke-width="traceNode.children.length !== 0 ? 2 : 0"
              :stroke="'gray'"
              @click="clickNode">
        <title>{{ `${traceNode.plans.length} plan(s)` }}</title>
      </circle>
      <text class="circle-text"
            text-anchor="middle"
            :transform="`translate(${[initialWidth/2, initialHeight/2+5]})`">{{ traceNode.plans.length }}</text>
      <text class="trace-node-text"
            text-anchor="start"
            :transform="textTransform">{{ traceNode.getSimpleName() }}</text>
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
      <TraceNodeVis v-for="(child, idx) in traceNode.children"
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
import {TraceNode, TraceTree} from "@/js/seq/TraceTree"

export default {
  name: 'TraceNodeVis',
  components: {
  },
  props: {
    traceTree: TraceTree,
    nodeIdx: Number,
    traceNode: TraceNode,
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
