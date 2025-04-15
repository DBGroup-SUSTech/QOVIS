<template>
  <svg class="vis-plan-node" :width="phaseGroup.width" :height="phaseGroup.height"
       @click="clickSvg">
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
<!--      <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">-->
<!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
<!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
<!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
<!--        <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>-->
<!--      </linearGradient>-->
<!--      <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">-->
<!--        <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>-->
<!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
<!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
<!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
<!--      </linearGradient>-->
<!--      <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">-->
<!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
<!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
<!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
<!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
<!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
<!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
<!--      </linearGradient>-->
    </defs>
<!--    <rect fill="#fafafa" rx="3" ry="3"-->
<!--          stroke="black" stroke-width="3"-->
<!--          :width="phaseGroup.width" :height="phaseGroup.height"></rect>-->
    <g v-for="(batchGroup, i) in phaseGroup.batchGroups" :key="i"
       :transform="'translate(' + [batchGroup.x, batchGroup.y] + ')'">
      <rect fill="#fafafa" rx="3" ry="3"
            stroke="black" stroke-width="2"
            :width="batchGroup.width" :height="batchGroup.height"></rect>

      <g v-if="!batchGroup.isSingleBatch">
        <text class="batch-label" font-size="20"
              :dx="batchGroup.width / 2" :dy="22"
              text-anchor="middle">
          {{ batchGroup.batchName }}
        </text>
      </g>
        <g v-for="(planDag, i) in batchGroup.planDags" :key="i"
           :transform="'translate(' + [planDag.x + 5, planDag.y + 5] + ')'">
          <!--      <rect fill="#fafafa" rx="3" ry="3"-->
          <!--            stroke="black" stroke-width="2"-->
          <!--            :width="plan.width" :height="plan.height"></rect>-->
          <g class="plan-group"
             @click="clickPlan(planDag, i)"
             :transform="'translate(' + [5, 5] + ')'">
            <g class="edge-group">
              <g v-for="(edge, i) in planDag.edges" :key="i">
                <path :d="edge.path" stroke-width="1" stroke="black" fill="none"/>
              </g>
            </g>
            <g class="node-group">
              <g v-for="(node, i) in planDag.nodes" :key="i" @click="clickNode(node)"
                 :transform="'translate(' + [node.x, node.y] + ')'">
                <rect :fill="getEvoFill(node.getEvoType())" rx="3" ry="3"
                      stroke="black"
                      :width="node.width" :height="node.height">
                  <title>{{ node.planNode.str }}</title>
                </rect>
                <text class="node-label" font-size="20"
                      :dx="node.width / 2" :dy="22"
                      text-anchor="middle">
                  {{ getNodeLabel(node) }}
                  <title>{{ node.planNode.str }}</title>
                </text>
              </g>
            </g>
          </g>
        </g>
        <g v-for="(act, i) in batchGroup.planActions" :key="'act' + i"
           :transform="'translate(' + [act.x - 5, act.y] + ')'"
           @click="clickAction(act)">
          <path :d="act.path" :fill="'gray'"
                stroke="black" stroke-width="1"/>
          <g v-for="(item, j) in act.actionItems" :key="'item' + j"
             :transform="'translate(' + [item.x, item.y] + ')'"
             @click="clickAction(act)">
            <rect x="0" y="0" :width="item.width" :height="item.height" rx="3" ry="3"
                  :fill="getMetaTypeColor(item.getMetaType())"
                  stroke="black" stroke-width="1"/>
            <text class="act-label" font-size="15"
                  :dx="item.width / 2"
                  :dy="configV1.arrow.paddingY + 15"
                  text-anchor="middle">
              {{ item.getChangeLabel() }}
            </text>
          </g>
        </g>
    </g>
  </svg>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'
import {getEvoTypeColor, getFadedColor} from "@/js/common"
import {PhaseGroup} from "@/js/native/PhaseGroup"

export default {
  name: 'PhaseGroup',
  props: {
    'phaseGroup': PhaseGroup,
  },
  components: {
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  methods: {
    clickSvg() {
      // console.log(this.visNode)
    },
    clickAction(act) {
      console.log(act)
    },
    clickPlan(planDag, i) {
      console.log(planDag.plan)
      console.log(this.phaseGroup.planActions[i])
      for (const info of planDag.plan.infoList) {
        console.log(info, JSON.stringify(Object.assign(info, {plan: 'hidden'})))
      }
      if (planDag.plan.infoList.length === 0) {
        console.log("Empty info list")
      }
    },
    clickNode(node) {
      console.log(node.toString())
      console.log(node.planNode.str)
      console.log(node)
    },
    getNodeLabel(vPlanNode) {
      if (!this.configV1.useOptAlias) {
        return vPlanNode.toLimitedString(this.configV1.plan.charLimit)
      }
      const alias = this.optInfoMap.get(vPlanNode.planNode.name)?.alias ?? '?'
      return vPlanNode.toAliasStr(alias)
    },
    getEvoFill(type) {
      switch (type) {
        case 'A': return 'url(#gradient-add)'
        case 'R': return 'url(#gradient-remove)'
        case 'AR': return 'url(#gradient-add-remove)'
        case 'U': return getEvoTypeColor('U')
      }
      return 'red'
    },
    getEvoTypeColor(type) {
      return getEvoTypeColor(type)
    },
    getMetaTypeColor(type) {
      return getFadedColor(type)
    }
  },
  computed: {
    ...mapState('native', {
      optInfoMap: state => state.optInfoMap,
      configV1: state => state.configV1,
    }),
  }
}
</script>

<style scoped>

</style>
