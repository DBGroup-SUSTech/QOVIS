<template>
  <svg class="vis-node" @click="clickSvg"
       :width="struct.width" :height="struct.height">
    <rect fill="#fafafa" rx="3" ry="3"
          stroke="black" stroke-width="3"
          :width="struct.width" :height="struct.height"></rect>
    <g :transform="'translate(' + [5, 5] + ')'">
      <g class="edge-group">
        <g v-for="(edge, i) in struct.edges" :key="i">
          <path :d="edge.path" stroke-width="1" stroke="black" fill="none"/>
        </g>
      </g>
      <g class="node-group">
        <g v-for="(node, i) in struct.nodes" :key="i" @click="clickNode(node)"
           :transform="'translate(' + [node.x - node.width / 2, node.y - node.height / 2] + ')'">
          <rect fill="#efefef" rx="3" ry="3"
                stroke="black"
                :width="node.width" :height="node.height">
            <title>{{ node.toFullString() }}</title>
          </rect>
          <text class="node-label" font-size="15" :dx="2" :dy="17">
            {{ node.toString() }}
            <title>{{ node.toFullString() }}</title>
          </text>
        </g>
      </g>
    </g>
  </svg>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'
import {TimelineRow} from "@/js/timeline/TimelineRow"
import {PlanStructure} from "@/js/timeline/PlanStructure"

export default {
  name: 'PlanSegment',
  props: {
    timelineRow: TimelineRow,
    index: Number,
    struct: PlanStructure,
  },
  components: {
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  methods: {
    clickSvg() {
      // console.log(this.visNode)
    },
    clickNode(node) {
      console.log(node.toString())
      console.log(node.toFullString())
      console.log(node)
    }
  },
  computed: {
    ...mapState('test', {}),
  }
}
</script>

<style scoped>
.dag-container {
  padding: 10px;
}
.dag-container >>> .tooltip {
  text-align: left;
  /*white-space: nowrap;*/
}
</style>
