<template>
  <div class="main-page">
    <div class="header">
      <h3 style="margin-right: 10px;">QOVIS</h3>
      <el-select v-model="exampleName" placeholder="" @change="exampleSelectionChange" :disabled="useCaseParam">
        <el-option
            v-for="exampleName in exampleList"
            :key="exampleName"
            :label="getExampleLabel(exampleName)"
            :value="exampleName">
        </el-option>
      </el-select>
      <!-- <el-switch v-model="showUnchangeLink"
                 active-text="Show unchange"
                 style="margin-left: 10px;"></el-switch>
      <el-switch v-model="toEnlarge"
                 active-text="Enlarge"
                 style="margin-left: 10px;"></el-switch>
      <el-switch v-model="hoverDelay"
                 active-text="Hover delay"
                 style="margin-left: 10px;"></el-switch> -->
<!--      <span style="margin-left: 50px;">FreqCost: {{ visTraceTree ? visTraceTree.freqCost : 0 }}</span>-->
<!--      <span style="margin-left: 20px;">TimeCost: {{ visTraceTree ? visTraceTree.timeCost : 0 }}</span>-->
      <!-- <el-button type="plain" style="margin-left: 50px;" @click="exportSvg">Export SVG</el-button> -->
    </div>
    <div class="main">
      <div class="overview-container" ref="container">
        <TraceNav :vis-trace-tree="visTraceTree"/>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import TraceNav from "@/components/seq-page/trace-nav-4/TraceNav"
import {downloadString, exportSVG} from "@/utils/Download"
import {CaseIdToName, ToCaseId} from "@/js/question/Problem"
import {changeTitle} from "@/utils/Title"

export default {
  name: 'TracePage',
  components: {
    TraceNav,
  },
  data() {
    return {
      useCaseParam: false,
    }
  },
  mounted() {
    this.useCaseParam = false
    this.initExampleList(() => {
      // get parma "case" from url
      const caseId = this.$route.query.case
      if (typeof caseId === 'string' && caseId !== '') {
        try {
          const id = parseInt(caseId)
          this.exampleName = this.getExampleNameByCaseId(id)
          this.useCaseParam = true
          this.exampleSelectionChange()
        } catch (e) {
          this.$message.error('Invalid case id: ' + e)
        }
      } else if (this.$route.query.example !== undefined) {
        this.exampleName = 'bug4-2' // hard code
        this.useCaseParam = true
        this.exampleSelectionChange()
      }
    })
    if (this.$route.query.method === 'qvm') {
      this.changeTransSupportState(false)
    } else {
      this.changeTransSupportState(true)
    }
    this.mountScrollContainer(this.$refs.container)
  },
  methods: {
    ...mapMutations('trace', [
      'changeExampleName',
      'changeShowEvoLabel',
      'changeShowUnchangeLink',
      'mountScrollContainer',
      'changeTransSupportState',
      'changeToEnlarge',
      'changeHoverDelay',
    ]),
    ...mapActions('trace', [
      'initExampleList',
      'changeExample',
    ]),
    exampleSelectionChange() {
      this.changeExample(this.exampleName)
    },
    getExampleNameByCaseId(caseId) {
      const exampleName = CaseIdToName[caseId]
      if (exampleName !== undefined) {
        return exampleName
      }
      this.$message.error('Invalid case id')
      return 'ssb-0'
    },
    // getExampleLabel(exampleName) {
    //   const caseId = ToCaseId[exampleName]
    //   if (caseId !== undefined) {
    //     return `Case ${caseId}`
    //   }
    //   if (exampleName.startsWith('ssb')) {
    //     return `ssb - ${exampleName.split('-')[1]}`
    //   }
    //   if (exampleName === 'bug4-2') {
    //     return 'Example'
    //   }
    //   return exampleName
    // },
    getExampleLabel(exampleName) {
      switch (exampleName) {
        case 'bug0-0': return 'bug0 - opt loop'
        case 'bug0-1': return 'bug0 - normal case'
        case 'bug1-0': return 'bug1 - wrong join removal'
        case 'bug4-0': return 'bug4 - hint loss'
        case 'bug4-1': return 'bug4 - normal case'
        case 'bug4-2': return 'bug4 - inefficient hint'
      }
      if (exampleName.startsWith('ssb')) {
        return `ssb - ${exampleName.split('-')[1]}`
      }
      return exampleName
    },
    exportSvg() {
      const svg = document.querySelector('#trace-svg')
      exportSVG(svg, 'output.svg')
    }
  },
  watch: {
    exampleName(val) {
      changeTitle(this.getExampleLabel(val))
    }
  },
  computed: {
    ...mapState('trace', {
      exampleList: state => state.exampleList,
      visTraceTree: state => state.visTraceTree,
    }),
    height() {
      return this.visTraceTree?.height ?? 0
    },
    width() {
      return this.visTraceTree?.width ?? 0
    },
    exampleName: {
      get() {
        return this.$store.state.trace.exampleName
      },
      set(val) {
        this.changeExampleName(val)
      }
    },
    showEvoLabel: {
      get() {
        return this.$store.state.trace.showEvoLabel
      },
      set(val) {
        this.changeShowEvoLabel(val)
      }
    },
    showUnchangeLink: {
      get() {
        return this.$store.state.trace.showUnchangeLink
      },
      set(val) {
        this.changeShowUnchangeLink(val)
      }
    },
    toEnlarge: {
      get() {
        return this.$store.state.trace.toEnlarge
      },
      set(val) {
        this.changeToEnlarge(val)
      }
    },
    hoverDelay: {
      get() {
        return this.$store.state.trace.hoverDelay
      },
      set(val) {
        this.changeHoverDelay(val)
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
.detailed-container {
  /*height: calc(100% - 144px);*/
  /*height: 100%;*/
  width: 100%;
  border-top: 4px solid #f5f5f5;
}
</style>
