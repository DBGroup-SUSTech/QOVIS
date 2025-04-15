<template>
  <div class="main-page">
    <div class="header">
      <el-select v-model="exampleName" placeholder="" @change="exampleSelectionChange">
        <el-option
            v-for="exampleName in exampleList"
            :key="exampleName"
            :label="exampleName"
            :value="exampleName">
        </el-option>
      </el-select>
      <el-switch v-model="showTimeCost"
                 active-text="Show time cost"
                 style="margin-left: 10px;"></el-switch>
      <span style="margin-left: 50px;">FreqCost: {{ traceTree ? traceTree.freqCost : 0 }}</span>
      <span style="margin-left: 20px;">TimeCost: {{ traceTree ? traceTree.timeCost : 0 }}</span>
    </div>
    <div class="main">
      <div class="overview-container" :style="{
        height: `${height}px`,
      }">
        <PatternTraceNav :trace-tree="traceTree"/>
      </div>
      <div class="detailed-container" :style="{
        height: `calc(100% - ${height + 4}px)`
      }">
        <PatternPlanView :trace-tree="traceTree"/>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import PatternTraceNav from "@/components/seq-page/trace-nav-2/PatternTraceNav"
import PatternPlanView from "@/components/seq-page/trace-nav-2/PatternPlanView"

export default {
  name: 'SeqPage',
  components: {
    PatternPlanView,
    PatternTraceNav
  },
  data() {
    return {
      localExampleName: '',
    }
  },
  mounted() {
    this.initExampleList()
  },
  methods: {
    ...mapMutations('seq', [
      'changeExampleName',
      'changeShowTimeCost',
    ]),
    ...mapActions('seq', [
      'initExampleList',
      'changeExample',
    ]),
    exampleSelectionChange() {
      this.changeExample(this.exampleName)
    }
  },
  watch: {
  },
  computed: {
    ...mapState('seq', {
      exampleList: state => state.exampleList,
      // traceTree: state => state.traceTree,
      traceTree: state => state.patternTraceTree,
    }),
    height() {
      return this.traceTree?.height ?? 0
    },
    width() {
      return this.traceTree?.width ?? 0
    },
    exampleName: {
      get() {
        return this.$store.state.seq.exampleName
      },
      set(val) {
        this.changeExampleName(val)
      }
    },
    showTimeCost: {
      get() {
        return this.$store.state.seq.showTimeCost
      },
      set(val) {
        this.changeShowTimeCost(val)
      }
    },
  }
}
</script>

<style scoped>
.main-page {
  overflow: hidden;
  height: 100%;
  width: 100%;
}

.header {
  height: 60px;
  width: 100%;
  background: #f5f5f5;

  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 0 10px;
}

.main {
  width: 100%;
  position: absolute;
  top: 60px;
  left: 0;
  bottom: 0;
}

.overview-container {
  /*height: 140px;*/
  width: 100%;

  overflow: auto;
}
.detailed-container {
  /*height: calc(100% - 144px);*/
  /*height: 100%;*/
  width: 100%;
  border-top: 4px solid #f5f5f5;
}
</style>
