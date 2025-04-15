<template>
  <div class="timeline-page">
    <div class="header">
      <el-select v-model="exampleName" placeholder="">
        <el-option
            v-for="exampleName in exampleList"
            :key="exampleName"
            :label="exampleName"
            :value="exampleName">
        </el-option>
      </el-select>
      <el-select v-model="summaryName" placeholder="No summary"
                 style="margin-left: 10px;">
        <el-option
            v-for="summaryName in summaryList"
            :key="summaryName"
            :label="summaryName"
            :value="summaryName">
        </el-option>
      </el-select>
      <span v-if="summaryData" style="margin-left: 10px;">
          Cost: {{ summaryData.cost }}
      </span>
      <span v-if="summaryData" style="margin-left: 10px;">
          Loss: {{ summaryData.loss }}
      </span>
      <el-switch active-text="Align" v-model="toAlign" style="margin: 0 30px 0 auto;"/>
    </div>
    <div class="main">
      <div class="sketch-container">
        <Sketch/>
      </div>
      <div class="trace-container">
        <div v-for="(timelineRow, i) in timelineRows" :key="i"
             class="row-container">
          <TimelineRow :timelineRow="timelineRow"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import Sketch from "@/components/timeline-page/sketch/Sketch"
import TimelineRow from "@/components/timeline-page/timeline/TimelineRow"

export default {
  name: 'TimelinePage',
  components: {
    TimelineRow,
    Sketch,
  },
  data() {
    return {
    }
  },
  mounted() {
    this.initExampleList()
  },
  methods: {
    ...mapMutations('timeline', [
      'changeExampleName',
      'changeSummaryName',
    ]),
    ...mapActions('timeline', [
      'initExampleList',
      'changeExample',
      'changeSummary',
    ]),
  },
  watch: {
    exampleName() {
      this.changeExample(this.exampleName)
    },
    summaryName() {
      this.changeSummary({
        exampleName: this.exampleName,
        summaryName: this.summaryName,
      })
    }
  },
  computed: {
    ...mapState('timeline', {
      exampleList: state => state.exampleList,
      summaryList: state => state.summaryList,
      summaryData: state => state.summaryData,
      sketchGraph: state => state.sketchGraph,
      sketchGraphSimpleMeta: state => state.sketchGraphSimpleMeta,
      plans: state => state.plans,
    }),
    exampleName: {
      get() {
        return this.$store.state.timeline.exampleName
      },
      set(val) {
        this.changeExampleName(val)
      }
    },
    summaryName: {
      get() {
        return this.$store.state.timeline.summaryName
      },
      set(val) {
        this.changeSummaryName(val)
      }
    },
    toAlign: {
      get() {
        return this.sketchGraphSimpleMeta?.toAlign
      },
      set(val) {
        this.sketchGraphSimpleMeta.toAlign = val
      }
    },
    timelineRows() {
      return this.sketchGraph?.simpleMeta?.timelineRows ?? []
    }
  }
}
</script>

<style scoped>
.timeline-page {
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
  height: calc(100% - 60px);
  position: absolute;
  top: 60px;
  left: 0;
  bottom: 0;

  display: flex;
  flex-wrap: nowrap;
  overflow-y: auto;
}

.sketch-container {
  width: 199px;
  height: fit-content;
  overflow-x: auto;
  overflow-y: visible;
}

.trace-container {
  width: calc(100% - 200px);
  height: fit-content;
  border-left: 1px solid gray;
  overflow-x: auto;
  overflow-y: visible;
}
.row-container {
  width: fit-content;
  border-bottom: 1px solid gray;
}
.row-container:last-child {
  border-bottom: none;
}
</style>
