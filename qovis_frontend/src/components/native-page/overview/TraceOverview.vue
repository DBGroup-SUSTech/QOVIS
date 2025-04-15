<template>
  <div class="trace-overview">
    <div class="phase-group-list">
      <div v-for="(phase, i) in phases" :key="i"
           class="phase-group"
           :style="{
              'border-width': getBorderWidth(phase) + 'px',
              'border-color': getStroke(phase),
           }" @click="clickPhase(phase)">
        <div style="font-size: 20px;">{{ phase.toString() }}</div>
        <div class="item-row">
          <div v-for="(item, j) in phase.items" :key="j"
               class="item-rect"
               :style="{
                   'border-width': item.borderWidth + 'px',
                   'background': item.color,
                 }"> {{ item.toString() }} </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'

export default {
  name: 'TraceOverview',
  components: {
  },
  data() {
    return {
      svgEl: null,
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    ...mapMutations('native', [
        'changePhaseVisible'
    ]),
    clickPhase(phase) {
      console.log(phase)
      this.changePhaseVisible(phase.phaseIndex)
    },
    getBorderWidth(phase) {
      return (this.phaseGroups[phase.phaseIndex].show ? 2 : 1) *phase.borderWidth
    },
    getStroke(phase) {
      return this.phaseGroups[phase.phaseIndex].show ? '#699bef' : 'gray'
    },
  },
  computed: {
    ...mapState('native', {
      overviewTrace: state => state.overviewTrace,
      phaseGroups: state => state.phaseGroups,
      configV1: state => state.configV1,
    }),
    phases() {
      return this.overviewTrace?.phases ?? []
    }
  }
}
</script>

<style scoped>
.trace-overview {
  padding: 10px;
  overflow: scroll;
}
.phase-group-list {
  padding: 10px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}
.phase-group {
  border-radius: 3px;
  margin: 5px;
  border: gray solid 1px;
  padding: 0 10px 10px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  cursor: pointer;
  transition: border-width 0.2s;
}
.item-row {
  display: flex;
  justify-content: center;
  align-items: center;
}
.item {
  margin: 10px 5px 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  /*position: relative;*/
}
.item-rect {
  padding: 5px 10px;
  border-radius: 3px;
  border: gray solid 1px;
  margin: 0 2px;
  /*position: relative;*/
}
</style>
