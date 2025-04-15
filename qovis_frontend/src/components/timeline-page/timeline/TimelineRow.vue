<template>
  <div class="timeline-row">
    <div v-for="(item, i) in timelineRow.timelineItems" :key="i"
         class="item-container">
      <div v-if="item.isEff"
           class="step-container">
        <span class="step-label"
              :style="{ background: getStepLabelBackground(item)}">
          {{ item.step.toString() }}
        </span>
      </div>
      <div class="struct-container"
           :style="getStructContainerStyle(item)">
        <PlanSegment v-if="item.isEff"
                     style="margin: 0 10px;"
                     :timelineRow="timelineRow" :index="i" :struct="item.structure"/>
        <div v-else style="margin: 0 10px;"></div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {TimelineRow} from "@/js/timeline/TimelineRow"
import PlanSegment from "@/components/timeline-page/nested/PlanSegment"
import {mapState} from "vuex"
import {getFadedColor} from "@/js/common"

export default {
  name: 'TimelineRow',
  components: {PlanSegment},
  props: {
    timelineRow: TimelineRow,
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  methods: {
    getStructContainerStyle(item) {
      if (this.toAlign) {
        return { width: (item.alignWidth + 10*2) + 'px' }
      }
      if (item.isEff) {
        return { width: (item.width + 10*2) + 'px' }
      } else {
        return { width: 0 }
      }
    },
    getStepLabelBackground(item) {
      return getFadedColor(item.getLastMeta().type)
    }
  },
  computed: {
    ...mapState('timeline', {
      sketchGraphSimpleMeta: state => state.sketchGraphSimpleMeta
    }),
    toAlign() {
      return this.sketchGraphSimpleMeta.toAlign
    }
  }
}
</script>

<style scoped>
/* shift mode start */
/*.timeline-row {*/
/*  display: flex;*/
/*  margin-top: 10px;*/
/*  margin-bottom: 10px;*/
/*  padding-left: 25px;*/
/*}*/
/*.item-container {*/
/*  position: relative;*/
/*  padding-top: 30px;*/
/*}*/
/*.step-container {*/
/*  position: absolute;*/
/*  top: 0;*/
/*}*/
/*.step-label {*/
/*  margin-left: calc(-50% - 0px);*/
/*  padding: 0 5px;*/
/*  width: 100%;*/
/*  background: #f5f5f5;*/
/*  border: 1px solid black;*/
/*  border-radius: 3px;*/
/*}*/
/* shift mode stop */

/* normal mode start */
.timeline-row {
  display: flex;
  margin-top: 10px;
  margin-bottom: 10px;
  padding-left: 5px;
}
.item-container {
  position: relative;
  padding-top: 30px;
}
.step-container {
  position: absolute;
  top: 0;
  width: 100%;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.step-label {
  max-width: calc(100% - 14px);
  padding: 0 5px;
  border: 1px solid black;
  border-radius: 3px;

  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
/* shift mode stop */

.struct-container {
  margin-top: 10px;
  transition: width 0.5s;
}
</style>
