<template>
  <div class="main-page">
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
    </div>
    <div class="main">
      <div class="overview-container">
        <TimelineOverview v-if="toMeta != null"/>
      </div>
      <div class="detailed-container">
<!--        <MainView/>-->
        <Nested/>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import MainView from "@/components/native-page/native/Native"
import Nested from "@/components/summary-page/nested/Nested"
import TimelineOverview from "@/components/common/TimelineOverview"

export default {
  name: 'SummaryPage',
  components: {
    TimelineOverview,
    Nested,
    MainView
  },
  data() {
    return {
    }
  },
  mounted() {
    this.initExampleList()
  },
  methods: {
    ...mapMutations('trace', [
      'changeExampleName',
      'changeSummaryName',
    ]),
    ...mapActions('trace', [
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
    },
  },
  computed: {
    ...mapState('trace', {
      exampleList: state => state.exampleList,
      summaryList: state => state.summaryList,
      summaryData: state => state.summaryData,
      toMeta: state => state.toMeta,
      detailedSGraphs: state => state.detailedSGraphs,
    }),
    exampleName: {
      get() {
        return this.$store.state.trace.exampleName
      },
      set(val) {
        this.changeExampleName(val)
      }
    },
    summaryName: {
      get() {
        return this.$store.state.trace.summaryName
      },
      set(val) {
        this.changeSummaryName(val)
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
  height: 140px;
  width: 100%;
  overflow: auto;
}
.detailed-container {
  height: calc(100% - 144px);
  /*height: 100%;*/
  width: 100%;
  overflow: auto;
  border-top: 4px solid #f5f5f5;
}
</style>
