<template>
  <g class="vis-node" @click="clickSvg">
    <rect fill="#fafafa" rx="3" ry="3"
          stroke="black" stroke-width="3"
          :width="visNode.width" :height="visNode.height"></rect>
    <g v-for="(plan, i) in visNode.visPlans" :key="i"
       :transform="'translate(' + [plan.x - plan.width / 2, plan.y - plan.height / 2] + ')'">
<!--      <rect fill="#fafafa" rx="3" ry="3"-->
<!--            stroke="black" stroke-width="2"-->
<!--            :width="plan.width" :height="plan.height"></rect>-->
      <g :transform="'translate(' + [5, 5] + ')'">
        <g class="edge-group">
          <g v-for="(edge, i) in plan.getEdges()" :key="i">
            <path :d="edge.path" stroke-width="1" stroke="black" fill="none"/>
          </g>
        </g>
        <g class="node-group">
          <g v-for="(node, i) in plan.visPlanNodes" :key="i" @click="clickNode(node)"
             :transform="'translate(' + [node.x - node.width / 2, node.y - node.height / 2] + ')'">
            <rect fill="#efefef" rx="3" ry="3"
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
    <g v-for="(tran, i) in visNode.visTrans" :key="'tran' + i"
       :transform="'translate(' + [tran.x - 10, tran.y - tran.height / 2] + ')'">
      <path :d="tran.path" :fill="getMetaTypeColor(tran.getMetaType())"
            stroke="black" stroke-width="1"/>
      <text class="tran-label" font-size="15"
            :dx="(tran.width - configV1.arrow.lengthPlus) / 2"
            :dy="configV1.arrow.widthPlus/2 + configV1.arrow.paddingY + 15"
            text-anchor="middle">
        {{ tran.getChangeLabel() }}
      </text>
    </g>
  </g>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex'
import {VisNode} from "@/js/main-view/VisNode"
import {getFadedColor} from "@/js/common"

export default {
  name: 'NestedDagNode',
  props: {
    'visNode': VisNode,
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
    clickNode(node) {
      console.log(node.toString())
      console.log(node.planNode.str)
      console.log(node)
    },
    getNodeLabel(visPlanNode) {
      if (!this.configV1.useOptAlias) {
        return visPlanNode.toString()
      }
      const alias = this.optInfoMap.get(visPlanNode.planNode.name)?.alias ?? '?'
      return visPlanNode.toAliasStr(alias)
    },
    getMetaTypeColor(type) {
      return getFadedColor(type)
    }
  },
  computed: {
    ...mapState('trace', {
      optInfoMap: state => state.optInfoMap,
      configV1: state => state.configV1,
    }),
  }
}
</script>

<style scoped>
.dag-container {
  padding: 10px;
}
.dag-container >>> .tooltip {
  text-align: left;
  /*white-space: nowrap;*/
}
</style>
