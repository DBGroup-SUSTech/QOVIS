<template>
  <div class="probe-line">
    <div>
      <span>{{index}} G={{probeLine.origin.gValue}}, H={{probeLine.origin.hValue}}, Rules={{probeLine.origin.rules}}</span>
    </div>
    <svg id="probe-svg" :width="width" :height="height">
      <defs>
        <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
          <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>
        </linearGradient>
        <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
          <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
        </linearGradient>
        <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
          <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
          <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
        </linearGradient>
      </defs>

      <g class="plan-dag-group">
        <PlanView v-for="(plan, i) in probeLine.plans" :key="i"
                  :plan="plan"/>
      </g>
      <g class="transform-lists-group">
        <g v-for="(transformList, i) in probeLine.transforms"
           :key="i"
           class="transform-list-group"
           :transform="`translate(${[planPadding, planPadding]})`">
          <g v-for="(transform, j) in transformList"
             :key="j"
             :transform="`translate(${[0, 0]})`"
             class="transform-item">
            <path v-show="transform.origin.type !== 'unchange' || showUnchangeLink"
                  :d="transform.path" stroke-width="2" :stroke="transform.color" fill="none">
              <title>{{ transform.type }}</title>
            </path>
          </g>
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import PlanView from "@/components/probe-page/PlanView"
import {VisProbeLine} from "@/js/probe/VisProbeLine"
import {getEvoTypeColor} from "@/js/common"

export default {
  name: 'ProbeLine',
  components: {
    PlanView,
  },
  props: {
    probeLine: VisProbeLine,
    index: Number,
  },
  data() {
    return {}
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    getPlanBlockName(block) {
      return `plan#${block.visPlan.origin.pid}`
    },
    getEvoTypeColor(type) {
      return getEvoTypeColor(type)
    },
  },
  computed: {
    ...mapState('probe', {
      planPadding: state => state.configV3.plan.padding,
      showUnchangeLink: state => state.showUnchangeLink,
    }),
    width() {
      return (this.probeLine?.width ?? 0)
    },
    height() {
      return (this.probeLine?.height ?? 0)
    },
  }
}
</script>

<style scoped>
.probe-line {
  padding: 10px;
}
</style>
