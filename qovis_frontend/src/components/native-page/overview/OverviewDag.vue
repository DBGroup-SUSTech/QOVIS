<template>
  <svg class="overview-svg" ref="svg">
    <line v-for="edge in edges" :key="edge.traceEdge.eid"
          :x1="edge.getSrc().x" :y1="edge.getSrc().y"
          :x2="edge.getDst().x" :y2="edge.getDst().y"
          :stroke="getEdgeColor(edge)" stroke-width="12">
      <title>{{ getEdgeTooltip(edge) }}</title>
    </line>
    <circle v-for="node in nodes" :key="node.traceNode.nid"
            :cx="node.x" :cy="node.y" :r="8"
            stroke="black" stroke-width="3" fill="white">
      <title>{{ getPlanTooltip(node) }}</title>
    </circle>
  </svg>
</template>

<script>
/* eslint-disable */
import {mapState} from "vuex"
import {getColor, getMetaItems, getPlanMetaItems} from "@/js/common"

export default {
  name: 'OverviewDag',
  components: {
  },
  data() {
    return {
      svgEl: null,
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    /**
     * @param {OverviewEdge} edge
     */
    getEdgeColor(edge) {
      return getColor(edge.traceEdge.meta.type)
    },
    getEdgeTooltip(edge) {
      const items = getMetaItems(edge.traceEdge.meta)
      return items.map(([k, v]) => `${k}: ${v}`).join('\n')
    },
    getPlanTooltip(node) {
      const items = getPlanMetaItems(node.traceNode.meta)
      return items.map(([k, v]) => `${k}: ${v}`).join('\n')
    }
  },
  watch: {
    overviewDag() {
      this.overviewDag.computeLayout({
        paddingX: 20,
        paddingY: 20,
        gapX: 30,
        gapY: 30,
      })
      const {width, height} = this.overviewDag
      this.svgEl.setAttribute('width', width)
      this.svgEl.setAttribute('height', height)
    }
  },
  computed: {
    ...mapState('trace', {
      overviewDag: state => state.overviewDag,
    }),
    nodes() {
      return this.overviewDag?.nodes ?? []
    },
    edges() {
      return this.overviewDag?.edges ?? []
    },
  }
}
</script>

<style scoped>
.overview-svg {
}
div.tooltip {
  position: absolute;
  text-align: center;
  padding: 2px;
  font: 20px sans-serif;
  border: gray solid 1px;
  border-radius: 4px;
  pointer-events: none;
  background: white;
}
</style>
