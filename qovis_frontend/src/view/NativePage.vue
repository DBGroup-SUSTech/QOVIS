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
    </div>
    <div class="main">
      <div class="overview-container">
        <TraceOverview/>
      </div>
      <div class="detailed-container">
        <Native/>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import Native from "@/components/native-page/native/Native"
import TraceOverview from "@/components/native-page/overview/TraceOverview"

export default {
  name: 'NativePage',
  components: {
    TraceOverview,
    Native,
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
    ...mapMutations('native', [
      'changeExampleName',
    ]),
    ...mapActions('native', [
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
    ...mapState('native', {
      exampleList: state => state.exampleList,
      overviewTrace: state => state.overviewTrace,
      phaseGroups: state => state.phaseGroups,
    }),
    exampleName: {
      get() {
        return this.$store.state.native.exampleName
      },
      set(val) {
        this.changeExampleName(val)
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
}
.detailed-container {
  height: calc(100% - 144px);
  /*height: 100%;*/
  width: 100%;
  border-top: 4px solid #f5f5f5;
}
</style>
