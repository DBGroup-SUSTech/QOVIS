<template>
  <path :d="path" fill="none" stroke="grey" :stroke-width="strokeWidth"></path>
</template>

<script>
import * as d3 from "d3"

export default {
  name: "DagEdge",
  props: ['edge'],
  data() {
    return {}
  },
  computed: {
    path() {
      // const src = this.edge.src;
      // const dst = this.edge.dst;
      // let startPoint = {x: src.x + src.width / 2, y: src.y}
      // let endPoint = {x: dst.x - dst.width / 2, y: dst.y}

      let points = [...this.edge.points]
      // points[0] = startPoint
      // points[points.length - 1] = endPoint

      var Gen = d3.line()
          .x((p) => p.x)
          .y((p) => p.y)
          .curve(d3.curveBasis)
      return Gen(points)
    },
    strokeWidth() {
      return 1;
    }
  }
}
</script>

<style scoped>

</style>
