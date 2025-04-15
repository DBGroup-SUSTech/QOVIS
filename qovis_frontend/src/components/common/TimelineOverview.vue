<template>
  <div class="timeline-overview">
<!--    <svg ref="svg" @click="clickSvg" :width="toMeta.width" :height="toMeta.height">-->
<!--      <g>-->
<!--        <g v-for="(phase, i) in toMeta.phases" :key="i"-->
<!--           class="phase-group"-->
<!--           :transform="'translate(' + [phase.x, phase.y] + ')'">-->
<!--          <rect x="0" y="0" :width="phase.width" :height="phase.height"-->
<!--                rx="3" ry="3" fill="none"-->
<!--                :stroke="getStroke(phase)" :stroke-width="phase.borderWidth"/>-->
<!--          <text :dx="phase.getTextX(configV1)" :dy="phase.getTextY(configV1)"-->
<!--                :font-size="configV1.timelineOverviewItem.fontSize">{{ phase.toString() }}</text>-->
<!--          <g v-for="(item, j) in phase.items" :key="j"-->
<!--             class="item-group"-->
<!--             :transform="'translate(' + [item.x, item.y] + ')'">-->
<!--            <rect v-for="(offset, k) in item.getCollapsedOffsets(configV1)" :key="k"-->
<!--                  :x="offset" y="0" :width="item.rectWidth" :height="item.height"-->
<!--                  rx="3" ry="3" :fill="item.color"-->
<!--                  stroke="grey" :stroke-width="item.borderWidth"/>-->
<!--            <text :dx="item.getTextX(configV1)" :dy="item.getTextY(configV1)"-->
<!--                  :font-size="configV1.timelineOverviewItem.fontSize">{{ item.toString() }}</text>-->
<!--          </g>-->
<!--        </g>-->
<!--      </g>-->
<!--    </svg>-->
    <div class="phase-group-list">
      <div v-for="(phase, i) in toMeta.phases" :key="i"
           class="phase-group"
           :style="{
              'border-width': getBorderWidth(phase) + 'px',
              'border-color': getStroke(phase),
           }" @click="clickPhase(phase)">
        <div style="font-size: 20px;">{{ phase.toString() }}</div>
        <div class="item-row">
          <div v-for="(item, j) in phase.items" :key="j"
               class="item">
            <span v-for="k in Array.from({length: item.collapseCnt}, (v, x) => x)" :key="k"
                 class="item-rect"
                 :style="{
                   'margin-left': ((item.collapseCnt - 1 - k) * 10) + 'px',
                   'margin-top': k === 0 ? '0' : '-36px',
                   'border-width': item.borderWidth + 'px',
                   'background': item.color,
                 }"> {{ getAlias(item.toString()) }} </span>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'

export default {
  name: 'TimelineOverview',
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
    ...mapMutations('trace', [
        'changeVisGraphVisible'
    ]),
    clickPhase(phase) {
      console.log(phase)
      this.changeVisGraphVisible(phase.phaseIndex)
    },
    getBorderWidth(phase) {
      return (this.visGraphs[phase.phaseIndex].show ? 2 : 1) * phase.borderWidth
    },
    getStroke(phase) {
      return this.visGraphs[phase.phaseIndex].show ? '#699bef' : 'gray'
    },
    getAlias(name) {
      return name.includes('JoinSelection') ? 'JoinSelection' : name
    }
  },
  computed: {
    ...mapState('trace', {
      visGraphs: state => state.visGraphs,
      toMeta: state => state.toMeta,
      configV1: state => state.configV1,
    }),
  }
}
</script>

<style scoped>
.timeline-overview {
  padding: 10px;
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
  /*position: relative;*/
}
</style>
