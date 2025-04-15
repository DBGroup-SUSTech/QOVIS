<template>
  <div class="native-view">
    <div class="seq-container">
      <div v-for="(group, i) in phaseGroups" :key="updateCnt + '-' + i"
           class="node-container"
           :style="{
            'width': group.show ? (group.width + 40) + 'px' : '0'
           }">
        <div class="plan-dag-container"
             :style="{
              'border-color': group.show ? 'grey' : 'white'
             }">
          <Phase :phaseGroup="group"></Phase>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from "vuex"
import Phase from "@/components/native-page/native/Phase"

export default {
  name: 'Native',
  components: {
    Phase,
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
    phaseGroups() {
      console.log(this.phaseGroups)
    }
  },
  computed: {
    ...mapState('native', {
      summaryData: state => state.summaryData,
      phaseGroups: state => state.phaseGroups,
    }),
  }
}
</script>

<style scoped>
.native-view {
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
