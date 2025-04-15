<template>
  <g class="vis-node" @click="click">
  </g>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'
import {SketchNode} from "@/js/timeline/SketchGraph"

export default {
  name: 'SketchNode',
  props: {
    'node': SketchNode,
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
    click() {
      // console.log(this.visNode)
    },
  },
  computed: {
    ...mapState('test', {}),
  }
}
</script>

<style scoped>

</style>
