<template>
  <div class="dag-container">
    <svg ref="svg" @click="clickSvg">
      <g class="edge-group">
        <g v-for="(edge, i) in edges" :key="i">
          <path :d="edge.path" stroke-width="3" stroke="black" fill="none"/>
        </g>
      </g>
      <g class="node-group">
        <g v-for="(node, i) in nodes" :key="i"
              :transform="'translate(' + [node.x - node.width / 2, node.y - node.height / 2] + ')'"
           @click="clickNode(node)">
          <NestedDagNode :visNode="node"/>
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'
import {VisGraph} from "@/js/main-view/VisGraph"
import NestedDagNode from "@/components/summary-page/nested/NestedDagNode"

export default {
  name: 'NestedDag',
  props: {
    'visGraph': VisGraph,
  },
  components: {
    NestedDagNode
  },
  data() {
    return {
      svgEl: null,
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
    this.svgEl.setAttribute('width', this.visGraph.width)
    this.svgEl.setAttribute('height', this.visGraph.height)
  },
  methods: {
    clickSvg() {
      console.log(this.visGraph)
    },
    clickNode(node) {
      console.log(node)
    }
  },
  computed: {
    ...mapState('test', {}),
    nodes() {
      return this.visGraph.nodes ?? []
    },
    edges() {
      return this.visGraph.getEdges() ?? []
    }
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
