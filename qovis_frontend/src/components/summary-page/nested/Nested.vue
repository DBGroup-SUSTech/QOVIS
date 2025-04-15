<template>
  <div class="nested-view">
    <div v-if="summaryData && summaryData.generateStrategy === 's'" class="seq-container">
      <div v-for="(visGraph, i) in visGraphs" :key="updateCnt + '-' + i"
           class="node-container"
           :style="{
            'width': visGraph.show ? (visGraph.width + 40) + 'px' : '0'
           }">
        <div class="plan-dag-container"
             :style="{
              'border-color': visGraph.show ? 'grey' : 'white'
             }">
          <NestedDag :visGraph="visGraph"></NestedDag>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from "vuex"
import NestedDag from "@/components/summary-page/nested/NestedDag"

export default {
  name: 'Nested',
  components: {
    NestedDag
  },
  data() {
    return {
      updateCnt: 0,
    }
  },
  mounted() {
  },
  methods: {
  },
  watch: {
    visGraphs() {
      console.log(this.visGraphs)
    }
  },
  computed: {
    ...mapState('trace', {
      visGraphs: state => state.visGraphs,
      summaryData: state => state.summaryData,
      toMeta: state => state.toMeta,
    }),
  }
}
</script>

<style scoped>
.nested-view {
  height: 100%;
  width: 100%;
  overflow: auto;
}
.seq-container{
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  height: 100%;
}
.node-container {
  display: flex;
  flex-direction: column;
  transition: width 0.5s, height 0.5s;
}
.plan-dag-container {
  width: calc(100% - 20px);
  border: 2px solid;
  margin: 10px;
  overflow: hidden;
  transition: border-color 0.5s;
}
</style>
