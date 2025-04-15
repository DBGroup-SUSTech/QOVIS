<template>
  <div class="sketch" v-if="sketchGraphSimpleMeta">
    <svg class="sketch-svg" ref="svg" @click="clickSvg"
         :width="sketchGraphSimpleMeta.width"
         :height="sketchGraphSimpleMeta.height">
      <g :transform="'translate(' + [10, 0] + ')'">
        <g class="edge-group"
           :transform="'translate(' + [5, 0] + ')'">
          <g v-for="(edgeMeta, i) in edgeMetas" :key="i">
            <path :d="edgeMeta.path" stroke-width="10" stroke="#cccccc" stroke-linecap="round" fill="none"/>
          </g>
        </g>
        <g class="node-group">
          <g v-for="(nodeMeta, i) in nodeMetas" :key="i" @click="clickNode(nodeMeta)"
             :transform="'translate(' + [nodeMeta.x - nodeMeta.width / 2,
                                       nodeMeta.y - nodeMeta.height / 2] + ')'">
            <rect fill="#efefef" rx="3" ry="3"
                  stroke="black"
                  :width="nodeMeta.width + 10" :height="nodeMeta.height">
              <title>{{ nodeMeta.sketchNode.type }}</title>
            </rect>
            <text class="node-label" font-size="20" :dx="10" :dy="22">
              {{ nodeMeta.sketchNode.type }}
              <title>{{ nodeMeta.sketchNode.type }}</title>
            </text>
          </g>
        </g>
      </g>

    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'

export default {
  name: 'Sketch',
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
      console.log(this.sketchGraphSimpleMeta)
    },
    clickNode(node) {
      console.log(node)
    }
  },
  computed: {
    ...mapState('timeline', {
      sketchGraphSimpleMeta: state => state.sketchGraphSimpleMeta,
    }),
    nodeMetas() {
      return this.sketchGraphSimpleMeta.nodeMetas
    },
    edgeMetas() {
      return this.sketchGraphSimpleMeta.edgeMetas
    }
  }
}
</script>

<style scoped>

</style>
