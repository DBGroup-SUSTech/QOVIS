<template>
  <div class="main-page">
    <div class="header">
      <el-select v-model="probeName" placeholder="" @change="exampleSelectionChange">
        <el-option
            v-for="name in probeList"
            :key="name"
            :label="name"
            :value="name">
        </el-option>
      </el-select>
      <el-switch v-model="showEvoLabel"
                 active-text="Show glyphs"
                 style="margin-left: 10px;"></el-switch>
      <el-switch v-model="showUnchangeLink"
                 active-text="Show unchange"
                 style="margin-left: 10px;"></el-switch>
      <!--      <span style="margin-left: 50px;">FreqCost: {{ visTraceTree ? visTraceTree.freqCost : 0 }}</span>-->
      <!--      <span style="margin-left: 20px;">TimeCost: {{ visTraceTree ? visTraceTree.timeCost : 0 }}</span>-->
      <el-button type="plain" style="margin-left: 50px;" @click="exportSvg">Export SVG</el-button>
    </div>
    <div class="main">
      <div class="overview-container">
        <div v-for="(line, i) in visProbeLines" :key="probeName + i"
             class="line-container" >
          <ProbeLine :probeLine="line" :index="i"></ProbeLine>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import TraceNav from "@/components/seq-page/trace-nav-4/TraceNav"
import {exportSVG} from "@/utils/Download"
import ProbeLine from "@/components/probe-page/ProbeLine"

export default {
  name: 'ProbePage',
  components: {
    ProbeLine,
    TraceNav,
  },
  data() {
    return {
    }
  },
  mounted() {
    this.initProbeList()
  },
  methods: {
    ...mapMutations('probe', [
      'changeProbeName',
      'changeShowEvoLabel',
      'changeShowUnchangeLink',
    ]),
    ...mapActions('probe', [
      'initProbeList',
      'changeProbe',
    ]),
    exampleSelectionChange() {
      this.changeProbe(this.probeName)
    },
    exportSvg() {
      const svg = document.querySelector('#trace-svg')
      exportSVG(svg, 'output.svg')
    }
  },
  watch: {
  },
  computed: {
    ...mapState('probe', {
      probeList: state => state.probeList,
      // data
      probeLines: state => state.probeLines,
      visProbeLines: state => state.visProbeLines,
    }),
    probeName: {
      get() {
        return this.$store.state.probe.probeName
      },
      set(val) {
        this.changeProbeName(val)
      }
    },
    showEvoLabel: {
      get() {
        return this.$store.state.probe.showEvoLabel
      },
      set(val) {
        this.changeShowEvoLabel(val)
      }
    },
    showUnchangeLink: {
      get() {
        return this.$store.state.probe.showUnchangeLink
      },
      set(val) {
        this.changeShowUnchangeLink(val)
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
  height: 100%;
  width: 100%;

  overflow: auto;
}
.line-container {
  overflow-x: scroll;
  overflow-y: hidden;
  width: 100%;
}
.detailed-container {
  /*height: calc(100% - 144px);*/
  /*height: 100%;*/
  width: 100%;
  border-top: 4px solid #f5f5f5;
}
</style>
