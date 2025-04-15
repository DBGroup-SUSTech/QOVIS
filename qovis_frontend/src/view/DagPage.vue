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
    </div>
    <div class="main">
      <div class="trace-container">
        <Native/>
      </div>
<!--      <div class="overview-container">-->
<!--      </div>-->
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapActions, mapMutations, mapState} from "vuex"
import Native from "@/components/native-page/native/Native"

export default {
  name: 'DagPage',
  components: {
    Native
  },
  data() {
    return {
    }
  },
  mounted() {
    this.initExampleList()
  },
  methods: {
    ...mapMutations('native', [
        'changeExampleName'
    ]),
    ...mapActions('native', [
        'initExampleList',
        'changeExample'
    ]),
  },
  watch: {
    exampleName() {
      this.changeExample(this.exampleName)
    }
  },
  computed: {
    ...mapState('native', {
      exampleList: state => state.exampleList,
      plans: state => state.plans,
    }),
    exampleName: {
      get() {
        return this.$store.state.native.exampleName
      },
      set(val) {
        this.changeExampleName(val)
      }
    }
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

.trace-container {
  height: 100%;
  width: 100%;
  overflow: auto;
}

.overview-container {
  height: 100%;
  width: 200px;
  overflow: auto;
  display: inline-block;
}
</style>
