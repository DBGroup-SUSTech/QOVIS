<template>
  <g :transform="'translate(' +  [node.x , node.y] + ')'">
    <rect :fill="fill" fill-opacity="0.5" rx="3" ry="3"
          :width="node.width" :height="node.height"
          :stroke-width="strokeWidth" :stroke="stroke"
    ></rect>
    <text class="title" font-size="12" text-anchor="middle" style="cursor: default">{{ node.name }}</text>
  </g>
</template>

<script>
import * as d3 from "d3"

export default {
  name: "DagNode",
  props: ['node'],
  mounted() {
    let title = d3.select(this.$el).select('.title');
    // let boundaryRect = title.node().getBoundingClientRect();
    let boundaryRect = title.node().getBBox();
    title.attr('dx', this.node.width / 2)
        .attr('dy', boundaryRect.height / 2 + this.node.height / 2 - 3);
  },
  computed: {
    stroke() {
      return 'grey'
    },
    strokeWidth() {
      return 1
    },
    fill() {
      console.log(this.node.marked)
      return this.node.marked ? '#8cb9dc' : '#f6f6f6'
    },
  },
  methods: {}
}
</script>

<style scoped>

</style>
